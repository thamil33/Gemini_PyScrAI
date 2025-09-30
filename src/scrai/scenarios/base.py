from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

from ..models import Action, Actor, Event, SimulationState


@dataclass(slots=True)
class ScenarioContext:
    """Carries the mutable state for a running scenario."""

    state: SimulationState
    actors: List[Actor] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)

    def extend(
        self,
        *,
        actors: Sequence[Actor] | None = None,
        events: Sequence[Event] | None = None,
        actions: Sequence[Action] | None = None,
    ) -> None:
        if actors:
            self.actors.extend(actors)
        if events:
            self.events.extend(events)
        if actions:
            self.actions.extend(actions)


class Scenario(ABC):
    """Base contract for scenario modules."""

    name: str

    @abstractmethod
    def seed(self, context: ScenarioContext) -> None:
        """Populate the initial context with actors, events, and actions."""

    def before_phase(self, context: ScenarioContext) -> None:  # pragma: no cover - optional hook
        """Hook executed before each phase starts."""

    def after_phase(self, context: ScenarioContext) -> None:  # pragma: no cover - optional hook
        """Hook executed after each phase completes."""

    def on_snapshot(self, context: ScenarioContext) -> None:  # pragma: no cover - optional hook
        """Hook executed when the simulation state is snapshotted."""


__all__ = ["Scenario", "ScenarioContext"]
