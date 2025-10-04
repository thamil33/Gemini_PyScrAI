from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Type

from .base import Scenario
from .registry import ScenarioRegistry
from .service import ScenarioService


def discover_scenarios() -> dict[str, Type[Scenario]]:
    """Automatically discover all scenario classes in the scenes directory."""
    scenarios = {}
    scenes_dir = Path(__file__).parent / "scenes"
    
    if not scenes_dir.exists():
        return scenarios

    for file_path in scenes_dir.glob("*.py"):
        if file_path.stem.startswith("_"):
            continue

        module_name = f"scrai.scenarios.scenes.{file_path.stem}"
        try:
            module = importlib.import_module(module_name)
            
            # Find all Scenario subclasses in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (
                    issubclass(obj, Scenario)
                    and obj is not Scenario
                    and hasattr(obj, "name")
                ):
                    scenarios[obj.name] = obj
        except Exception as e:
            # Log but don't fail if a scenario module has issues
            print(f"Warning: Failed to load scenario from {file_path}: {e}")
    
    return scenarios


def create_default_scenario_service() -> ScenarioService:
    registry = ScenarioRegistry()
    
    # Auto-discover and register all scenarios
    discovered = discover_scenarios()
    for name, scenario_class in discovered.items():
        registry.register(name, scenario_class())
    
    return ScenarioService(registry=registry)


__all__ = ["create_default_scenario_service", "discover_scenarios"]
