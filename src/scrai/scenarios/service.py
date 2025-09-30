from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from ..models import Action, Actor, Event, SimulationState
from .base import Scenario, ScenarioContext
from .registry import ScenarioRegistry


@dataclass(slots=True)
class ScenarioService:
    registry: ScenarioRegistry

    def select(self, key: str) -> Optional[Scenario]:
        return self.registry.get(key)

    def seed_scenario(self, key: str, state: SimulationState) -> ScenarioContext:
        scenario = self.registry.get(key)
        if scenario is None:
            raise ValueError(f"Scenario '{key}' is not registered")

        context = ScenarioContext(state=state)
        scenario.seed(context)
        return context

    def before_phase(self, scenario: Scenario, context: ScenarioContext) -> None:
        scenario.before_phase(context)

    def after_phase(self, scenario: Scenario, context: ScenarioContext) -> None:
        scenario.after_phase(context)

    def on_snapshot(self, scenario: Scenario, context: ScenarioContext) -> None:
        scenario.on_snapshot(context)


__all__ = ["ScenarioService"]
