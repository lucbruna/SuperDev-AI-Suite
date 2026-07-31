"""Entity model."""

from __future__ import annotations

import time
import uuid
from typing import Any


class EntityModel:
    def __init__(self) -> None:
        self._entities: dict[str, dict[str, Any]] = {}

    def create(self, name: str, entity_type: str = "generic", attributes: dict[str, Any] = None) -> dict[str, Any]:
        entity_id = str(uuid.uuid4())[:8]
        entity = {
            "entity_id": entity_id,
            "name": name,
            "type": entity_type,
            "attributes": attributes or {},
            "created_at": time.time(),
        }
        self._entities[entity_id] = entity
        return entity

    def get(self, entity_id: str) -> dict[str, Any]:
        return self._entities.get(entity_id, {"error": "not_found"})

    def update(self, entity_id: str, attributes: dict[str, Any]) -> bool:
        if entity_id not in self._entities:
            return False
        self._entities[entity_id]["attributes"].update(attributes)
        return True

    def delete(self, entity_id: str) -> bool:
        if entity_id in self._entities:
            del self._entities[entity_id]
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._entities.values())

    def list_by_type(self, entity_type: str) -> list[dict[str, Any]]:
        return [e for e in self._entities.values() if e.get("type") == entity_type]

    def search(self, query: str) -> list[dict[str, Any]]:
        return [
            e
            for e in self._entities.values()
            if query.lower() in str(e.get("name", "")).lower() or query.lower() in str(e.get("attributes", {})).lower()
        ]

    def count(self) -> int:
        return len(self._entities)
