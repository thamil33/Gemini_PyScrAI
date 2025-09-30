from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable

DEFAULT_STATE_PATH = Path.home() / ".scrai" / "state.json"


class LocalStateStore:
    """Lightweight JSON-backed store for CLI state persistence."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_STATE_PATH
        self._data: Dict[str, Dict[str, Any]] = {
            "simulations": {},
            "actors": {},
            "events": {},
            "actions": {},
        }
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
                if isinstance(raw, dict):
                    for key in self._data:
                        collection = raw.get(key, {})
                        if isinstance(collection, dict):
                            self._data[key] = collection
        except json.JSONDecodeError:
            # Corrupted file; keep in-memory defaults
            pass

    def _sync(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self._data, handle, indent=2, sort_keys=True)

    def put(self, collection: str, entity_id: str, payload: Dict[str, Any]) -> None:
        self._data.setdefault(collection, {})[entity_id] = payload
        self._sync()

    def bulk_put(self, collection: str, items: Dict[str, Dict[str, Any]]) -> None:
        self._data[collection] = items
        self._sync()

    def get(self, collection: str, entity_id: str) -> Dict[str, Any] | None:
        return self._data.get(collection, {}).get(entity_id)

    def list(self, collection: str) -> Iterable[Dict[str, Any]]:
        return self._data.get(collection, {}).values()

    def delete(self, collection: str, entity_id: str) -> bool:
        bucket = self._data.get(collection, {})
        if entity_id in bucket:
            bucket.pop(entity_id)
            self._sync()
            return True
        return False

    def exists(self, collection: str, entity_id: str) -> bool:
        return entity_id in self._data.get(collection, {})

    def collection_items(self, collection: str) -> Dict[str, Dict[str, Any]]:
        return self._data.get(collection, {})
