from __future__ import annotations

from .scenes.simple_town import SimpleTownScenario
from .registry import ScenarioRegistry
from .service import ScenarioService


def create_default_scenario_service() -> ScenarioService:
    registry = ScenarioRegistry()
    registry.register(SimpleTownScenario.name, SimpleTownScenario())
    return ScenarioService(registry=registry)


__all__ = ["create_default_scenario_service"]
