"""Shared dependencies for API endpoints."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..cli.runtime import RuntimeContext
from ..config import load_settings
from ..data.action_repository import ActionRepository
from ..data.actor_repository import ActorRepository
from ..data.event_repository import EventRepository
from ..data.firestore_client import FirestoreClient
from ..data.simulation_repository import SimulationRepository
from ..engine import PhaseEngine
from ..llm import LLMService, LLMServiceConfig
from ..scenarios import create_default_scenario_service
from ..cli.memory import (
    MemoryActionRepository,
    MemoryActorRepository,
    MemoryEventRepository,
    MemorySimulationRepository,
)
from ..cli.store import LocalStateStore, DEFAULT_STATE_PATH


logger = logging.getLogger(__name__)


class RuntimeManager:
    """Manages singleton runtime instances with per-simulation locks."""
    
    def __init__(self) -> None:
        self._runtime: Optional[RuntimeContext] = None
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._stream_subscribers: dict[str, set[asyncio.Queue[Dict[str, Any]]]] = {}
        self._stream_lock = asyncio.Lock()
    
    async def initialize(self, backend: str = "memory") -> None:
        """Initialize the runtime context."""
        if self._runtime is not None:
            return
        
        async with self._global_lock:
            if self._runtime is not None:
                return
            
            settings = load_settings()
            scenario_service = create_default_scenario_service()

            try:
                llm_config = LLMServiceConfig.from_env()
                llm_service: Optional[LLMService] = LLMService(llm_config)
            except Exception as exc:  # pragma: no cover - configuration edge cases
                logger.warning("Failed to initialize LLM service: %s", exc)
                llm_service = None
            
            if backend == "firestore":
                firestore_client = FirestoreClient(
                    project_id=settings.firestore.project_id,
                    credentials_path=settings.firestore.credentials_path,
                )
                await firestore_client.initialize()
                
                actor_repo: Union[ActorRepository, MemoryActorRepository] = ActorRepository(firestore_client)
                event_repo: Union[EventRepository, MemoryEventRepository] = EventRepository(firestore_client)
                action_repo: Union[ActionRepository, MemoryActionRepository] = ActionRepository(firestore_client)
                simulation_repo: Union[SimulationRepository, MemorySimulationRepository] = SimulationRepository(firestore_client)
            else:
                # Memory backend
                state_path = DEFAULT_STATE_PATH
                store = LocalStateStore(state_path)
                actor_repo = MemoryActorRepository(store)
                event_repo = MemoryEventRepository(store)
                action_repo = MemoryActionRepository(store)
                simulation_repo = MemorySimulationRepository(store)
            
            phase_engine = PhaseEngine(
                simulation_repository=simulation_repo,  # type: ignore
                actor_repository=actor_repo,  # type: ignore
                event_repository=event_repo,  # type: ignore
                action_repository=action_repo,  # type: ignore
                llm_service=llm_service,
                scenario_service=scenario_service,
            )
            
            self._runtime = RuntimeContext(
                backend=backend,
                simulation_repository=simulation_repo,  # type: ignore
                actor_repository=actor_repo,  # type: ignore
                event_repository=event_repo,  # type: ignore
                action_repository=action_repo,  # type: ignore
                phase_engine=phase_engine,
                scenario_service=scenario_service,
                llm_service=llm_service,
                state_path=DEFAULT_STATE_PATH,
                settings=settings,
            )
    
    async def shutdown(self) -> None:
        """Cleanup runtime resources."""
        async with self._stream_lock:
            self._stream_subscribers.clear()
        # Future: close database connections, etc.
    
    def get_runtime(self) -> RuntimeContext:
        """Get the initialized runtime context."""
        if self._runtime is None:
            raise RuntimeError("Runtime not initialized")
        return self._runtime
    
    def get_simulation_lock(self, simulation_id: str) -> asyncio.Lock:
        """Get or create a lock for a specific simulation."""
        if simulation_id not in self._locks:
            self._locks[simulation_id] = asyncio.Lock()
        return self._locks[simulation_id]

    async def subscribe_to_stream(self, simulation_id: str) -> asyncio.Queue[Dict[str, Any]]:
        """Register an SSE subscriber queue for a simulation."""

        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=32)
        async with self._stream_lock:
            subscribers = self._stream_subscribers.setdefault(simulation_id, set())
            subscribers.add(queue)
        return queue

    async def unsubscribe_from_stream(
        self,
        simulation_id: str,
        queue: asyncio.Queue[Dict[str, Any]],
    ) -> None:
        """Remove the SSE subscriber queue for a simulation."""

        async with self._stream_lock:
            subscribers = self._stream_subscribers.get(simulation_id)
            if not subscribers:
                return
            subscribers.discard(queue)
            if not subscribers:
                self._stream_subscribers.pop(simulation_id, None)

    async def publish_stream_event(self, simulation_id: str, event: Dict[str, Any]) -> None:
        """Broadcast an event to all SSE subscribers for a simulation."""

        async with self._stream_lock:
            subscribers = list(self._stream_subscribers.get(simulation_id, set()))

        if not subscribers:
            return

        for queue in subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    logger.warning(
                        "Dropping SSE event for simulation %s: subscriber queue full",
                        simulation_id,
                    )


# Global singleton instance
_runtime_manager: Optional[RuntimeManager] = None


def get_runtime_manager() -> RuntimeManager:
    """Get or create the global runtime manager."""
    global _runtime_manager
    if _runtime_manager is None:
        _runtime_manager = RuntimeManager()
    return _runtime_manager
