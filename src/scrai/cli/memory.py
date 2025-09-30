from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, TypeVar, Generic, Callable

from ..data.repository import Repository
from ..models import Action, Actor, Event, SimulationState
from ..models.action import ActionPriority, ActionStatus, ActionType
from ..models.actor import ActorType
from ..models.event import EventStatus, EventType
from ..models.simulation_state import SimulationPhase, SimulationStatus
from .store import LocalStateStore

T = TypeVar("T")
JsonDict = Dict[str, Any]


class MemoryRepository(Generic[T], Repository[T]):
    """Generic in-memory repository persisted via LocalStateStore."""

    def __init__(
        self,
        *,
        collection: str,
        store: LocalStateStore,
        to_dict: Callable[[T], JsonDict],
        from_dict: Callable[[JsonDict], T],
    ) -> None:
        self._collection = collection
        self._store = store
        self._to_dict = to_dict
        self._from_dict = from_dict

    async def create(self, entity: T) -> str:
        payload = self._to_dict(entity)
        entity_id = payload["id"]
        self._store.put(self._collection, entity_id, payload)
        return entity_id

    async def get(self, entity_id: str) -> Optional[T]:
        payload = self._store.get(self._collection, entity_id)
        return self._from_dict(payload) if payload else None

    async def update(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        payload = self._store.get(self._collection, entity_id)
        if payload is None:
            return False
        merged = {**payload, **updates}
        self._store.put(self._collection, entity_id, merged)
        return True

    async def delete(self, entity_id: str) -> bool:
        return self._store.delete(self._collection, entity_id)

    async def list_all(self, limit: Optional[int] = None) -> List[T]:
        items = [self._from_dict(item) for item in self._store.list(self._collection)]
        return items[:limit] if limit else items

    async def query(self, filters: Dict[str, Any], limit: Optional[int] = None) -> List[T]:
        results: List[T] = []
        for item in self._store.list(self._collection):
            if all(item.get(field) == value for field, value in filters.items()):
                results.append(self._from_dict(item))
                if limit and len(results) >= limit:
                    break
        return results

    async def exists(self, entity_id: str) -> bool:
        return self._store.exists(self._collection, entity_id)


class MemoryActorRepository(MemoryRepository[Actor]):
    def __init__(self, store: LocalStateStore) -> None:
        super().__init__(
            collection="actors",
            store=store,
            to_dict=lambda actor: actor.to_dict(),
            from_dict=Actor.from_dict,
        )

    async def find_by_type(self, actor_type: ActorType, limit: Optional[int] = None) -> List[Actor]:
        return await self.query({"type": actor_type.value}, limit)

    async def find_by_name(self, name: str) -> Optional[Actor]:
        results = await self.query({"name": name}, limit=1)
        return results[0] if results else None

    async def find_active(self, limit: Optional[int] = None) -> List[Actor]:
        return await self.query({"active": True}, limit)


class MemoryEventRepository(MemoryRepository[Event]):
    def __init__(self, store: LocalStateStore) -> None:
        super().__init__(
            collection="events",
            store=store,
            to_dict=lambda event: event.to_dict(),
            from_dict=Event.from_dict,
        )

    async def find_by_status(self, status: EventStatus, limit: Optional[int] = None) -> List[Event]:
        return await self.query({"status": status.value}, limit)

    async def find_by_type(self, event_type: EventType, limit: Optional[int] = None) -> List[Event]:
        return await self.query({"type": event_type.value}, limit)


class MemoryActionRepository(MemoryRepository[Action]):
    def __init__(self, store: LocalStateStore) -> None:
        super().__init__(
            collection="actions",
            store=store,
            to_dict=lambda action: action.to_dict(),
            from_dict=Action.from_dict,
        )

    async def find_by_actor(self, actor_id: str, limit: Optional[int] = None) -> List[Action]:
        return await self.query({"actor_id": actor_id}, limit)

    async def find_by_status(self, status: ActionStatus, limit: Optional[int] = None) -> List[Action]:
        return await self.query({"status": status.value}, limit)


class MemorySimulationRepository(MemoryRepository[SimulationState]):
    def __init__(self, store: LocalStateStore) -> None:
        super().__init__(
            collection="simulations",
            store=store,
            to_dict=lambda sim: sim.to_dict(),
            from_dict=SimulationState.from_dict,
        )

    async def update(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        # Ensure we refresh updated_at when not provided
        if "updated_at" not in updates:
            updates["updated_at"] = datetime.utcnow().isoformat()
        return await super().update(entity_id, updates)

    async def find_by_status(self, status: SimulationStatus, limit: Optional[int] = None) -> List[SimulationState]:
        return await self.query({"status": status.value}, limit)

    async def find_by_scenario(self, scenario_module: str, limit: Optional[int] = None) -> List[SimulationState]:
        return await self.query({"scenario_module": scenario_module}, limit)

    async def find_running(self, limit: Optional[int] = None) -> List[SimulationState]:
        return await self.find_by_status(SimulationStatus.RUNNING, limit)

    async def find_completed(self, limit: Optional[int] = None) -> List[SimulationState]:
        return await self.find_by_status(SimulationStatus.COMPLETED, limit)

    async def find_by_name(self, name: str) -> Optional[SimulationState]:
        results = await self.query({"name": name}, limit=1)
        return results[0] if results else None


__all__ = [
    "MemoryActorRepository",
    "MemoryEventRepository",
    "MemoryActionRepository",
    "MemorySimulationRepository",
]
