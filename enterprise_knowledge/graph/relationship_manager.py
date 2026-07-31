"""Relationship management for the Knowledge Graph."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_models import (KnowledgeNode,
                                                   RelationshipRecord,
                                                   RelationshipType)
from enterprise_knowledge.knowledge_protocols import new_id


class RelationshipManager:
    """CRUD over graph edges via the shared registry."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry

    def create(self, source_id: str, target_id: str,
               rel_type: RelationshipType = RelationshipType.CONNECTED_TO,
               properties: dict[str, Any] | None = None) -> RelationshipRecord | None:
        if self.registry is not None and (
                self.registry.get_node(source_id) is None or
                self.registry.get_node(target_id) is None):
            return None
        relationship = RelationshipRecord(
            relationship_id=new_id("relationship"), source_id=source_id,
            target_id=target_id, rel_type=rel_type,
            properties=dict(properties or {}))
        if self.registry is not None:
            self.registry.register_relationship(relationship)
        return relationship

    def get(self, relationship_id: str) -> RelationshipRecord | None:
        if self.registry is None:
            return None
        return self.registry.get_relationship(relationship_id)

    def list(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_relationships()

    def all(self) -> list[RelationshipRecord]:
        if self.registry is None:
            return []
        return self.registry.relationships()

    def by_source(self, source_id: str) -> list[RelationshipRecord]:
        return [r for r in self.all() if r.source_id == source_id]

    def by_target(self, target_id: str) -> list[RelationshipRecord]:
        return [r for r in self.all() if r.target_id == target_id]

    def between(self, source_id: str, target_id: str) -> list[RelationshipRecord]:
        return [r for r in self.all()
                if r.source_id == source_id and r.target_id == target_id]

    def remove(self, relationship_id: str) -> bool:
        if self.registry is None:
            return False
        return self.registry.remove_relationship(relationship_id)

    def count(self) -> int:
        return len(self.list())

    def neighbors(self, node_id: str) -> list[dict[str, Any]]:
        result = []
        for relationship in self.all():
            if relationship.source_id == node_id:
                result.append({"node_id": relationship.target_id,
                               "direction": "out",
                               "rel_type": relationship.rel_type.value,
                               "relationship_id": relationship.relationship_id})
            elif relationship.target_id == node_id:
                result.append({"node_id": relationship.source_id,
                               "direction": "in",
                               "rel_type": relationship.rel_type.value,
                               "relationship_id": relationship.relationship_id})
        return result

    def outgoing(self, node_id: str) -> list[dict[str, Any]]:
        return [n for n in self.neighbors(node_id) if n["direction"] == "out"]
