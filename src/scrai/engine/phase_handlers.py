"""Phase handler implementations for the ScrAI simulation engine."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence

from ..models import Action, Actor, Event, SimulationState
from ..models.action import ActionStatus
from ..models.simulation_state import SimulationPhase, SimulationStatus
from ..scenarios import ScenarioContext
from .context import PhaseContext, PhaseResult

logger = logging.getLogger(__name__)


class BasePhaseHandler(ABC):
    """Abstract base class for all phase handlers."""

    phase: SimulationPhase

    def __init__(self, *, name: Optional[str] = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    async def run(self, context: PhaseContext) -> PhaseResult:
        """Execute the phase and return the resulting state."""

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"{self.__class__.__name__}(phase={self.phase})"


class PhaseHandlerRegistry:
    """Registry mapping simulation phases to handler implementations."""

    def __init__(self, handlers: Iterable[BasePhaseHandler]):
        self._handlers: Dict[SimulationPhase, BasePhaseHandler] = {}
        for handler in handlers:
            if handler.phase in self._handlers:
                raise ValueError(f"Multiple handlers registered for phase {handler.phase}")
            self._handlers[handler.phase] = handler

    def get(self, phase: SimulationPhase) -> BasePhaseHandler:
        try:
            return self._handlers[phase]
        except KeyError as exc:
            raise KeyError(f"No handler registered for phase {phase}") from exc

    def phases(self) -> List[SimulationPhase]:  # pragma: no cover - trivial
        return list(self._handlers.keys())


class InitializePhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.INITIALIZE

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        if simulation.status == SimulationStatus.CREATED:
            simulation.start()
            notes.append("Simulation started")
        elif simulation.status == SimulationStatus.PAUSED:
            simulation.resume()
            notes.append("Simulation resumed from paused state")

        simulation.current_phase = SimulationPhase.INITIALIZE
        simulation.updated_at = datetime.utcnow()
        notes.append("Initialization phase complete")

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.EVENT_GENERATION,
            notes=notes,
        )


class EventGenerationPhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.EVENT_GENERATION

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []
        generated_event_ids: List[str] = []
        generated_action_ids: List[str] = []

        scenario_service = context.scenario_service
        if scenario_service is None:
            notes.append(
                "No scenario service configured; skipping scenario-driven event generation."
            )
        else:
            scenario_key = simulation.scenario_module
            scenario = scenario_service.select(scenario_key)

            if scenario is None:
                notes.append(
                    f"Scenario '{scenario_key}' is not registered; skipping scenario seeding."
                )
            else:
                scenario_metadata = simulation.metadata.setdefault("scenario", {})
                seeded = bool(scenario_metadata.get("seeded"))
                base_actor_ids: set[str]
                base_event_ids: set[str]
                base_action_ids: set[str]

                if not seeded:
                    scenario_context = scenario_service.seed_scenario(scenario_key, simulation)
                    base_actor_ids = set()
                    base_event_ids = set()
                    base_action_ids = set()
                    notes.append(f"Scenario '{scenario_key}' seeded with initial entities.")
                else:
                    scenario_context = await self._build_context_from_state(context)
                    base_actor_ids = {actor.id for actor in scenario_context.actors}
                    base_event_ids = {event.id for event in scenario_context.events}
                    base_action_ids = {action.id for action in scenario_context.actions}
                    notes.append(f"Scenario context loaded for '{scenario_key}'.")

                scenario_service.before_phase(scenario, scenario_context)

                new_actors = [actor for actor in scenario_context.actors if actor.id not in base_actor_ids]
                new_events = [event for event in scenario_context.events if event.id not in base_event_ids]
                new_actions = [action for action in scenario_context.actions if action.id not in base_action_ids]

                if new_actors or new_events or new_actions:
                    event_ids, action_ids = await self._persist_generated_entities(
                        context,
                        scenario_context.state,
                        new_actors,
                        new_events,
                        new_actions,
                    )
                    generated_event_ids.extend(event_ids)
                    generated_action_ids.extend(action_ids)
                    if new_actors:
                        notes.append(
                            f"Registered {len(new_actors)} new actors from scenario '{scenario_key}'."
                        )
                    if new_events:
                        notes.append(f"Generated {len(new_events)} scenario-driven events.")
                    if new_actions:
                        notes.append(f"Generated {len(new_actions)} scenario-driven actions.")
                else:
                    notes.append(f"Scenario '{scenario_key}' produced no new entities this cycle.")

                scenario_service.after_phase(scenario, scenario_context)

                if not seeded:
                    scenario_metadata.update(
                        {
                            "seeded": True,
                            "scenario_key": scenario_key,
                            "seeded_at": datetime.utcnow().isoformat(),
                        }
                    )
                scenario_metadata["last_event_generation_at"] = datetime.utcnow().isoformat()

        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.ACTION_COLLECTION,
            notes=notes,
            generated_event_ids=generated_event_ids,
            generated_action_ids=generated_action_ids,
        )

    async def _build_context_from_state(self, context: PhaseContext) -> ScenarioContext:
        scenario_context = ScenarioContext(state=context.simulation)

        actors: List[Actor] = []
        for actor_id in context.simulation.active_actor_ids:
            actor = await context.actor_repository.get(actor_id)
            if actor:
                actors.append(actor)

        events: List[Event] = []
        for event_id in context.simulation.pending_event_ids:
            event = await context.event_repository.get(event_id)
            if event:
                events.append(event)

        actions: List[Action] = []
        for action_id in context.simulation.pending_action_ids:
            action = await context.action_repository.get(action_id)
            if action:
                actions.append(action)

        scenario_context.extend(actors=actors, events=events, actions=actions)
        return scenario_context

    async def _persist_generated_entities(
        self,
        context: PhaseContext,
        simulation: SimulationState,
        new_actors: Sequence[Actor],
        new_events: Sequence[Event],
        new_actions: Sequence[Action],
    ) -> tuple[List[str], List[str]]:
        generated_event_ids: List[str] = []
        generated_action_ids: List[str] = []

        for actor in new_actors:
            exists = await context.actor_repository.exists(actor.id)
            if not exists:
                await context.actor_repository.create(actor)
            simulation.add_actor(actor.id)

        for event in new_events:
            exists = await context.event_repository.exists(event.id)
            if not exists:
                await context.event_repository.create(event)
            simulation.add_pending_event(event.id)
            generated_event_ids.append(event.id)

        for action in new_actions:
            exists = await context.action_repository.exists(action.id)
            if not exists:
                await context.action_repository.create(action)
            simulation.add_pending_action(action.id)
            generated_action_ids.append(action.id)

        return generated_event_ids, generated_action_ids


class ActionCollectionPhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.ACTION_COLLECTION

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        pending_actions = await context.action_repository.list_all(limit=None)
        simulation.pending_action_ids = [
            action.id
            for action in pending_actions
            if action.status not in {ActionStatus.COMPLETED, ActionStatus.CANCELLED}
        ]
        notes.append(
            f"Tracked {len(simulation.pending_action_ids)} pending actions for resolution."
        )
        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.ACTION_RESOLUTION,
            notes=notes,
        )


class ActionResolutionPhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.ACTION_RESOLUTION

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        # Placeholder: actual resolution logic will apply action outcomes and create events
        if simulation.pending_action_ids:
            notes.append(
                "Action resolution placeholder executed (apply LLM-driven resolution logic here)."
            )
        else:
            notes.append("No actions queued for resolution.")

        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.WORLD_UPDATE,
            notes=notes,
        )


class WorldUpdatePhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.WORLD_UPDATE

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        # Placeholder: apply effects of resolved events to actors and world state
        if simulation.pending_event_ids:
            notes.append("World update placeholder executed (apply event effects here).")
        else:
            notes.append("No pending events to apply to world state.")

        simulation.pending_event_ids = []
        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.SNAPSHOT,
            notes=notes,
        )


class SnapshotPhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.SNAPSHOT

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        simulation.record_snapshot()
        notes.append("Snapshot recorded.")
        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.EVENT_GENERATION,
            notes=notes,
        )
