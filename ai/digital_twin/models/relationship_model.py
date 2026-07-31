"""Relationship model."""

from __future__ import annotations

import time
import uuid
from typing import Any


class RelationshipModel:
    def __init__(self) -> None:
        self._relationships: list[dict[str, Any]] = []

    def create(
        self, source: str, target: str, relation_type: str = "related_to", attributes: dict[str, Any] = None
    ) -> dict[str, Any]:
        rel_id = str(uuid.uuid4())[:8]
        rel = {
            "rel_id": rel_id,
            "source": source,
            "target": target,
            "type": relation_type,
            "attributes": attributes or {},
            "created_at": time.time(),
        }
        self._relationships.append(rel)
        return rel

    def get_between(self, entity_id: str) -> list[dict[str, Any]]:
        return [r for r in self._relationships if r["source"] == entity_id or r["target"] == entity_id]

    def get_by_type(self, relation_type: str) -> list[dict[str, Any]]:
        return [r for r in self._relationships if r["type"] == relation_type]

    def delete(self, rel_id: str) -> bool:
        original = len(self._relationships)
        self._relationships = [r for r in self._relationships if r["rel_id"] != rel_id]
        return len(self._relationships) < original

    def list_all(self) -> list[dict[str, Any]]:
        return self._relationships

    def count(self) -> int:
        return len(self._relationships)
