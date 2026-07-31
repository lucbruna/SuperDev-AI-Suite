from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import Entity, Relation


class KnowledgeGraph:
    """In-memory knowledge graph with entities and typed relations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.knowledge_graph.graph")
        self._entities: dict[str, Entity] = {}
        self._relations: list[Relation] = []

    def add_entity(self, entity: Entity) -> None:
        if entity.name not in self._entities:
            self._entities[entity.name] = entity

    def add_relation(self, relation: Relation) -> None:
        self.add_entity(Entity(name=relation.source, entity_type="concept"))
        self.add_entity(Entity(name=relation.target, entity_type="concept"))
        for existing in self._relations:
            if (existing.source == relation.source and existing.target == relation.target
                    and existing.relation_type == relation.relation_type):
                return
        self._relations.append(relation)

    def get_entity(self, name: str) -> Entity | None:
        return self._entities.get(name)

    def entities(self) -> list[Entity]:
        return list(self._entities.values())

    def relations(self, entity_name: str | None = None) -> list[Relation]:
        if entity_name is None:
            return list(self._relations)
        return [
            relation
            for relation in self._relations
            if relation.source == entity_name or relation.target == entity_name
        ]

    def neighbors(self, entity_name: str) -> list[str]:
        neighbors: set[str] = set()
        for relation in self._relations:
            if relation.source == entity_name:
                neighbors.add(relation.target)
            if relation.target == entity_name:
                neighbors.add(relation.source)
        return sorted(neighbors)

    def count(self) -> dict[str, int]:
        return {"entities": len(self._entities), "relations": len(self._relations)}

    def clear(self) -> None:
        self._entities.clear()
        self._relations.clear()
