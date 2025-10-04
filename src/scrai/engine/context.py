"""Shared context objects used by phase handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..data import Repository
from ..llm import LLMService
from ..scenarios import ScenarioService
from ..models import Action, Actor, Event, SimulationState
from ..models.simulation_state import SimulationPhase


@dataclass(slots=True)
class PhaseContext:
    """Context passed to each phase handler."""

    simulation: SimulationState
    simulation_repository: Repository[SimulationState]
    actor_repository: Repository[Actor]
    event_repository: Repository[Event]
    action_repository: Repository[Action]
    llm_service: Optional[LLMService] = None
    scenario_service: Optional[ScenarioService] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def phase(self) -> SimulationPhase:
        return self.simulation.current_phase

    def with_simulation(self, simulation: SimulationState) -> "PhaseContext":
        """Return a new context with an updated simulation state."""
        return PhaseContext(
            simulation=simulation,
            simulation_repository=self.simulation_repository,
            actor_repository=self.actor_repository,
            event_repository=self.event_repository,
            action_repository=self.action_repository,
            llm_service=self.llm_service,
            scenario_service=self.scenario_service,
            metadata=self.metadata,
        )


@dataclass(slots=True)
class PhaseResult:
    """Result returned by a phase handler."""

    simulation: SimulationState
    executed_phase: SimulationPhase
    next_phase: SimulationPhase
    generated_event_ids: List[str] = field(default_factory=list)
    generated_action_ids: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def add_note(self, message: str) -> None:
        self.notes.append(message)
