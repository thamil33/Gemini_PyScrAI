"""Core phase engine implementation for ScrAI."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from ..scenarios import ScenarioService

from ..data import Repository
from ..llm import LLMService
from ..models.simulation_state import SimulationPhase, SimulationStatus
from ..models import Action, Actor, Event, SimulationState
from .context import PhaseContext, PhaseResult
from .exceptions import PhaseEngineError, PhaseExecutionError
from .phase_handlers import (
    ActionCollectionPhaseHandler,
    ActionResolutionPhaseHandler,
    EventGenerationPhaseHandler,
    InitializePhaseHandler,
    PhaseHandlerRegistry,
    SnapshotPhaseHandler,
    WorldUpdatePhaseHandler,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PhaseEngineConfig:
    """Configuration values for the phase engine."""

    persist_phase_notes: bool = True
    enforce_phase_sequence: bool = True
    max_consecutive_failures: int = 3


_DEFAULT_PHASE_ORDER: Sequence[SimulationPhase] = (
    SimulationPhase.INITIALIZE,
    SimulationPhase.EVENT_GENERATION,
    SimulationPhase.ACTION_COLLECTION,
    SimulationPhase.ACTION_RESOLUTION,
    SimulationPhase.WORLD_UPDATE,
    SimulationPhase.SNAPSHOT,
)


class PhaseEngine:
    """Coordinates execution of simulation phases."""

    def __init__(
        self,
        *,
        simulation_repository: Repository[SimulationState],
        actor_repository: Repository[Actor],
        event_repository: Repository[Event],
        action_repository: Repository[Action],
        llm_service: Optional[LLMService] = None,
        scenario_service: Optional["ScenarioService"] = None,
        handlers: Optional[Iterable] = None,
        config: Optional[PhaseEngineConfig] = None,
    ) -> None:
        self._simulation_repository = simulation_repository
        self._actor_repository = actor_repository
        self._event_repository = event_repository
        self._action_repository = action_repository
        self._llm_service = llm_service
        self._scenario_service = scenario_service
        self._config = config or PhaseEngineConfig()

        handler_instances = list(handlers) if handlers else self._default_handlers()
        self._registry = PhaseHandlerRegistry(handler_instances)
        self._phase_order = _DEFAULT_PHASE_ORDER
        self._lock = asyncio.Lock()

    async def step(
        self,
        simulation_id: str,
        *,
        force_phase: Optional[SimulationPhase] = None,
    ) -> PhaseResult:
        """Execute a single phase for the specified simulation."""

        async with self._lock:
            simulation = await self._load_simulation(simulation_id)
            phase_to_run = force_phase or simulation.current_phase

            if simulation.status in {SimulationStatus.COMPLETED, SimulationStatus.ERROR}:
                raise PhaseExecutionError(
                    f"Simulation is in terminal state '{simulation.status.value}'.",
                    simulation_id=simulation_id,
                    phase=simulation.status.value,
                )

            self._verify_phase_allowed(phase_to_run, simulation)

            handler = self._registry.get(phase_to_run)
            context = PhaseContext(
                simulation=simulation,
                simulation_repository=self._simulation_repository,
                actor_repository=self._actor_repository,
                event_repository=self._event_repository,
                action_repository=self._action_repository,
                llm_service=self._llm_service,
                scenario_service=self._scenario_service,
            )

            logger.debug("Running phase %s for simulation %s", phase_to_run.value, simulation_id)
            result = await handler.run(context)

            await self._apply_phase_result(simulation_id, result)
            logger.info(
                "Completed phase %s for simulation %s -> next phase %s",
                result.executed_phase.value,
                simulation_id,
                result.next_phase.value,
            )

            return result

    async def run_cycle(self, simulation_id: str) -> List[PhaseResult]:
        """Execute a full cycle of phases (initialize through snapshot)."""

        results: List[PhaseResult] = []
        for _ in range(len(self._phase_order)):
            simulation = await self._load_simulation(simulation_id)
            if simulation.status in {SimulationStatus.COMPLETED, SimulationStatus.ERROR}:
                break

            phase = simulation.current_phase
            if phase not in self._phase_order:
                logger.warning(
                    "Simulation %s is in phase %s which is outside the canonical cycle.",
                    simulation_id,
                    phase.value,
                )
                break

            result = await self.step(simulation_id, force_phase=phase)
            results.append(result)

            if result.next_phase in {SimulationPhase.COMPLETED, SimulationPhase.PAUSED}:
                break
            if result.executed_phase == SimulationPhase.SNAPSHOT:
                break

        return results

    async def _load_simulation(self, simulation_id: str) -> SimulationState:
        simulation = await self._simulation_repository.get(simulation_id)
        if simulation is None:
            raise PhaseEngineError(
                f"Simulation '{simulation_id}' not found.",
                simulation_id=simulation_id,
            )
        return simulation

    def _verify_phase_allowed(self, phase: SimulationPhase, simulation: SimulationState) -> None:
        if not self._config.enforce_phase_sequence:
            return

        if phase not in self._phase_order:
            raise PhaseExecutionError(
                f"Phase {phase.value} is not part of the configured sequence.",
                simulation_id=simulation.id,
                phase=phase.value,
            )

        expected_phase = simulation.current_phase
        if phase != expected_phase:
            raise PhaseExecutionError(
                f"Attempted to run phase {phase.value} but simulation is expecting {expected_phase.value}.",
                simulation_id=simulation.id,
                phase=phase.value,
            )

    async def _apply_phase_result(self, simulation_id: str, result: PhaseResult) -> None:
        simulation = result.simulation

        if self._config.persist_phase_notes and result.notes:
            entry = {
                "phase": result.executed_phase.value,
                "timestamp": datetime.utcnow().isoformat(),
                "notes": result.notes,
            }
            history = simulation.metadata.get("phase_log", [])
            history.append(entry)
            simulation.metadata["phase_log"] = history

        self._update_cycle_progress(simulation, result)
        await self._persist_simulation(simulation_id, simulation)

    def _update_cycle_progress(self, simulation: SimulationState, result: PhaseResult) -> None:
        executed_phase = result.executed_phase
        next_phase = result.next_phase

        if executed_phase == SimulationPhase.SNAPSHOT:
            simulation.phase_number += 1

            if simulation.phase_number >= simulation.max_phases:
                simulation.complete()
                next_phase = SimulationPhase.COMPLETED

        if simulation.status == SimulationStatus.RUNNING:
            simulation.current_phase = next_phase
        elif simulation.status == SimulationStatus.COMPLETED:
            simulation.current_phase = SimulationPhase.COMPLETED

        simulation.updated_at = datetime.utcnow()

    async def _persist_simulation(self, simulation_id: str, simulation: SimulationState) -> None:
        try:
            updated = await self._simulation_repository.update(simulation_id, simulation.to_dict())
            if not updated:
                raise PhaseEngineError(
                    "Simulation document was not updated (possibly missing).",
                    simulation_id=simulation_id,
                )
        except Exception as exc:  # pragma: no cover - persistence failure path
            logger.error(
                "Failed to persist simulation %s after phase execution: %s",
                simulation_id,
                exc,
                exc_info=exc,
            )
            raise PhaseEngineError(
                "Failed to persist simulation state.",
                simulation_id=simulation_id,
            ) from exc

    def _default_handlers(self) -> Iterable:
        return (
            InitializePhaseHandler(),
            EventGenerationPhaseHandler(),
            ActionCollectionPhaseHandler(),
            ActionResolutionPhaseHandler(),
            WorldUpdatePhaseHandler(),
            SnapshotPhaseHandler(),
        )
