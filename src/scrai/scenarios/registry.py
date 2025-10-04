from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Type

from .base import Scenario


@dataclass(slots=True)
class ScenarioMetadata:
    key: str
    scenario: Scenario


class ScenarioRegistry:
    """Registry for available scenarios."""

    def __init__(self) -> None:
        self._scenarios: Dict[str, ScenarioMetadata] = {}

    def register(self, key: str, scenario: Scenario) -> None:
        normalized = key.strip().lower()
        if normalized in self._scenarios:
            raise ValueError(f"Scenario '{key}' is already registered")
        self._scenarios[normalized] = ScenarioMetadata(key=normalized, scenario=scenario)

    def unregister(self, key: str) -> None:
        normalized = key.strip().lower()
        self._scenarios.pop(normalized, None)

    def get(self, key: str) -> Optional[Scenario]:
        normalized = key.strip().lower()
        metadata = self._scenarios.get(normalized)
        return metadata.scenario if metadata else None

    def items(self) -> Iterable[Scenario]:
        for metadata in self._scenarios.values():
            yield metadata.scenario

    def list_all(self) -> list[dict[str, str]]:
        """List all registered scenarios with metadata."""
        scenarios = []
        for key, metadata in sorted(self._scenarios.items()):
            scenario = metadata.scenario
            # Get description from docstring or use a default
            description = (
                scenario.__class__.__doc__.strip().split("\n")[0]
                if scenario.__class__.__doc__
                else f"{scenario.__class__.__name__} scenario"
            )
            
            scenarios.append({
                "name": key,
                "display_name": scenario.__class__.__name__.replace("Scenario", "").replace("_", " ").title(),
                "description": description,
            })
        
        return scenarios


__all__ = ["ScenarioRegistry", "ScenarioMetadata"]
