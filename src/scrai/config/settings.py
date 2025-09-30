from __future__ import annotations

import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping, Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_CONFIG_PATHS: tuple[Path, ...] = (Path("config/settings.toml"),)


class FirestoreSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    project_id: str | None = Field(default=None, description="Firestore project identifier")
    credentials_path: str | None = Field(default=None, description="Path to service account credentials")


class LLMProviderSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(default=None, description="Human readable provider name")
    model: str | None = Field(default=None, description="Default model identifier")
    base_url: str | None = Field(default=None, description="Override base URL for OpenAI-compatible endpoints")
    api_key: str | None = Field(default=None, description="API key value")
    api_key_env: str | None = Field(default=None, description="Environment variable containing API key")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retries for requests")
    default_headers: Dict[str, str] = Field(default_factory=dict, description="Additional headers to include")


class LLMSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    primary_provider: str = Field(default="openrouter", description="Primary provider key")
    providers: Dict[str, LLMProviderSettings] = Field(default_factory=dict, description="Configured providers")


class SimulationSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    scenario_module: str = Field(default="simple_town", description="Default scenario module key")
    max_phases: int = Field(default=20, description="Default maximum phase count")
    auto_approve_events: bool = Field(default=False)
    auto_approve_actions: bool = Field(default=False)
    researcher_mode: bool = Field(default=True)


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    firestore: FirestoreSettings = Field(default_factory=FirestoreSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    simulation: SimulationSettings = Field(default_factory=SimulationSettings)


def _deep_merge(target: MutableMapping[str, object], updates: Mapping[str, object]) -> MutableMapping[str, object]:
    for key, value in updates.items():
        if isinstance(value, Mapping) and isinstance(target.get(key), Mapping):
            nested_target = target.setdefault(key, {})  # type: ignore[assignment]
            _deep_merge(nested_target, value)  # type: ignore[arg-type]
        else:
            target[key] = value  # type: ignore[index]
    return target


def _set_nested(mapping: MutableMapping[str, object], path: Sequence[str], value: object) -> None:
    current: MutableMapping[str, object] = mapping
    for key in path[:-1]:
        next_value = current.get(key)
        if not isinstance(next_value, MutableMapping):
            next_value = {}
            current[key] = next_value  # type: ignore[index]
        current = next_value  # type: ignore[assignment]
    current[path[-1]] = value  # type: ignore[index]


def _parse_env_value(raw: str) -> object:
    lowered = raw.lower()
    if lowered in {"true", "1", "yes", "on"}:
        return True
    if lowered in {"false", "0", "no", "off"}:
        return False
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


_ENV_PATHS: dict[str, tuple[str, ...]] = {
    "SCRAI_FIRESTORE_PROJECT_ID": ("firestore", "project_id"),
    "SCRAI_FIRESTORE_CREDENTIALS": ("firestore", "credentials_path"),
    "SCRAI_SIMULATION_SCENARIO": ("simulation", "scenario_module"),
    "SCRAI_SIMULATION_MAX_PHASES": ("simulation", "max_phases"),
    "SCRAI_SIMULATION_AUTO_APPROVE_EVENTS": ("simulation", "auto_approve_events"),
    "SCRAI_SIMULATION_AUTO_APPROVE_ACTIONS": ("simulation", "auto_approve_actions"),
    "SCRAI_SIMULATION_RESEARCHER_MODE": ("simulation", "researcher_mode"),
    "SCRAI_LLM_PRIMARY_PROVIDER": ("llm", "primary_provider"),
}


def load_settings(
    *,
    config_paths: Optional[Sequence[Path]] = None,
    environment: Mapping[str, str] | None = None,
) -> Settings:
    environment = environment or os.environ
    effective_paths = tuple(config_paths) if config_paths else DEFAULT_CONFIG_PATHS

    base = Settings()
    merged: MutableMapping[str, object] = base.model_dump(mode="python")

    for path in effective_paths:
        if path.exists():
            with path.open("rb") as handle:
                data = tomllib.load(handle)
            if isinstance(data, dict):
                _deep_merge(merged, data)

    for env_key, target_path in _ENV_PATHS.items():
        if env_key in environment:
            _set_nested(merged, target_path, _parse_env_value(environment[env_key]))

    settings = Settings.model_validate(merged)

    for provider in settings.llm.providers.values():
        if provider.api_key_env and not provider.api_key:
            api_key = environment.get(provider.api_key_env)
            if api_key:
                provider.api_key = api_key

    return settings


@lru_cache(maxsize=4)
def get_settings(*, config_paths: Optional[Sequence[Path]] = None) -> Settings:
    key = tuple(str(path) for path in (config_paths or DEFAULT_CONFIG_PATHS))
    return load_settings(config_paths=[Path(p) for p in key])
