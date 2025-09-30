from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from dotenv import load_dotenv

from ..config import Settings, load_settings
from ..data.action_repository import ActionRepository
from ..data.actor_repository import ActorRepository
from ..data.event_repository import EventRepository
from ..data.firestore_client import FirestoreClient
from ..data.repository import Repository
from ..data.simulation_repository import SimulationRepository
from ..engine import PhaseEngine
from ..llm import LLMService
from ..models import Action, Actor, Event, SimulationState
from ..scenarios import ScenarioService, create_default_scenario_service
from .memory import (
    MemoryActionRepository,
    MemoryActorRepository,
    MemoryEventRepository,
    MemorySimulationRepository,
)
from .store import DEFAULT_STATE_PATH, LocalStateStore


@dataclass
class RuntimeContext:
    backend: str
    simulation_repository: Repository[SimulationState]
    actor_repository: Repository[Actor]
    event_repository: Repository[Event]
    action_repository: Repository[Action]
    phase_engine: PhaseEngine
    scenario_service: ScenarioService | None
    llm_service: Optional[LLMService]
    state_path: Path
    settings: Settings


async def _build_firestore_runtime(
    *,
    project_id: Optional[str],
    credentials_path: Optional[str],
    scenario_service: ScenarioService,
    llm_service: Optional[LLMService],
) -> tuple[
    SimulationRepository,
    ActorRepository,
    EventRepository,
    ActionRepository,
    PhaseEngine,
]:
    firestore_client = FirestoreClient(project_id=project_id, credentials_path=credentials_path)
    await firestore_client.initialize()

    actor_repository = ActorRepository(firestore_client)
    event_repository = EventRepository(firestore_client)
    action_repository = ActionRepository(firestore_client)
    simulation_repository = SimulationRepository(firestore_client)

    phase_engine = PhaseEngine(
        simulation_repository=simulation_repository,
        actor_repository=actor_repository,
        event_repository=event_repository,
        action_repository=action_repository,
        llm_service=llm_service,
        scenario_service=scenario_service,
    )

    return simulation_repository, actor_repository, event_repository, action_repository, phase_engine


async def _build_memory_runtime(
    *,
    state_path: Path,
    scenario_service: ScenarioService,
    llm_service: Optional[LLMService],
) -> tuple[
    MemorySimulationRepository,
    MemoryActorRepository,
    MemoryEventRepository,
    MemoryActionRepository,
    PhaseEngine,
]:
    store = LocalStateStore(state_path)
    actor_repository = MemoryActorRepository(store)
    event_repository = MemoryEventRepository(store)
    action_repository = MemoryActionRepository(store)
    simulation_repository = MemorySimulationRepository(store)

    phase_engine = PhaseEngine(
        simulation_repository=simulation_repository,
        actor_repository=actor_repository,
        event_repository=event_repository,
        action_repository=action_repository,
        llm_service=llm_service,
        scenario_service=scenario_service,
    )

    return simulation_repository, actor_repository, event_repository, action_repository, phase_engine


def build_runtime(
    *,
    backend: str = "memory",
    state_path: Optional[Path] = None,
    project_id: Optional[str] = None,
    credentials_path: Optional[str] = None,
    scenario_service: Optional[ScenarioService] = None,
    llm_service: Optional[LLMService] = None,
    config_paths: Optional[Sequence[Path]] = None,
) -> RuntimeContext:
    load_dotenv()
    settings = load_settings(config_paths=config_paths)
    scenario_service = scenario_service or create_default_scenario_service()
    resolved_llm = llm_service

    if backend == "firestore":
        resolved_project = project_id or settings.firestore.project_id
        resolved_credentials = credentials_path or settings.firestore.credentials_path
        (
            simulation_repository,
            actor_repository,
            event_repository,
            action_repository,
            phase_engine,
        ) = asyncio.run(
            _build_firestore_runtime(
                project_id=resolved_project,
                credentials_path=resolved_credentials,
                scenario_service=scenario_service,
                llm_service=resolved_llm,
            )
        )
        state_path = state_path or DEFAULT_STATE_PATH
        return RuntimeContext(
            backend="firestore",
            simulation_repository=simulation_repository,
            actor_repository=actor_repository,
            event_repository=event_repository,
            action_repository=action_repository,
            phase_engine=phase_engine,
            scenario_service=scenario_service,
            llm_service=resolved_llm,
            state_path=state_path,
            settings=settings,
        )

    state_path = state_path or DEFAULT_STATE_PATH
    (
        simulation_repository,
        actor_repository,
        event_repository,
        action_repository,
        phase_engine,
    ) = asyncio.run(
        _build_memory_runtime(
            state_path=state_path,
            scenario_service=scenario_service,
            llm_service=resolved_llm,
        )
    )

    return RuntimeContext(
        backend="memory",
        simulation_repository=simulation_repository,
        actor_repository=actor_repository,
        event_repository=event_repository,
        action_repository=action_repository,
        phase_engine=phase_engine,
        scenario_service=scenario_service,
        llm_service=resolved_llm,
        state_path=state_path,
        settings=settings,
    )


__all__ = ["RuntimeContext", "build_runtime"]
