"""Relationship model."""
from __future__ import annotations
from typing import Any, Dict, List
import time, uuid

class RelationshipModel:
    def __init__(self) -> None:
        self._relationships: List[Dict[str, Any]] = []
    def create(self, source: str, target: str, relation_type: str = "related_to", attributes: Dict[str, Any] = None) -> Dict[str, Any]:
        rel_id = str(uuid.uuid4())[:8]
        rel = {"rel_id": rel_id, "source": source, "target": target, "type": relation_type, "attributes": attributes or {}, "created_at": time.time()}
        self._relationships.append(rel)
        return rel
    def get_between(self, entity_id: str) -> List[Dict[str, Any]]:
        return [r for r in self._relationships if r["source"] == entity_id or r["target"] == entity_id]
    def get_by_type(self, relation_type: str) -> List[Dict[str, Any]]:
        return [r for r in self._relationships if r["type"] == relation_type]
    def delete(self, rel_id: str) -> bool:
        original = len(self._relationships)
        self._relationships = [r for r in self._relationships if r["rel_id"] != rel_id]
        return len(self._relationships) < original
    def list_all(self) -> List[Dict[str, Any]]:
        return self._relationships
    def count(self) -> int:
        return len(self._relationships)
