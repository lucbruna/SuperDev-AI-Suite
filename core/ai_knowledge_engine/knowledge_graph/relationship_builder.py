from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from enum import Enum
from typing import Any


class RelationshipType(Enum):
    DEPENDS_ON = "depends_on"
    CONTAINS = "contains"
    RELATES_TO = "relates_to"
    CAUSES = "causes"
    IMPLEMENTS = "implements"
    REQUIRES = "requires"
    PRODUCES = "produces"


INFERRED_RELATION_MAP: dict[str, list[tuple[str, RelationshipType]]] = {
    "source_code": [
        ("compiled_binary", RelationshipType.PRODUCES),
        ("library", RelationshipType.DEPENDS_ON),
    ],
    "documentation": [
        ("source_code", RelationshipType.RELATES_TO),
        ("api_reference", RelationshipType.CONTAINS),
    ],
    "bug_report": [
        ("source_code", RelationshipType.RELATES_TO),
        ("feature_request", RelationshipType.RELATES_TO),
    ],
    "feature_request": [
        ("source_code", RelationshipType.REQUIRES),
    ],
}


class RelationshipBuilder:
    def __init__(self) -> None:
        self._relationships: list[dict[str, Any]] = []
        self._graph: dict[str, list[tuple[str, RelationshipType]]] = defaultdict(list)

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        rel = {
            "source_id": source_id,
            "target_id": target_id,
            "type": relationship_type.value,
            "properties": properties or {},
        }
        self._relationships.append(rel)
        self._graph[source_id].append((target_id, relationship_type))
        return rel

    async def infer_relationship(self, source_label: str, target_label: str) -> list[dict[str, Any]]:
        await asyncio.sleep(0.01)
        inferred: list[dict[str, Any]] = []
        if source_label in INFERRED_RELATION_MAP:
            for possible_target, rel_type in INFERRED_RELATION_MAP[source_label]:
                if possible_target == target_label:
                    inferred.append({
                        "source_label": source_label,
                        "target_label": target_label,
                        "inferred_type": rel_type.value,
                        "confidence": 0.8,
                    })
        return inferred

    async def batch_create(self, relationships: list[dict[str, Any]]) -> list[dict[str, Any]]:
        await asyncio.sleep(0.01)
        results: list[dict[str, Any]] = []
        for rel in relationships:
            rel_type_str = rel.get("type", "relates_to")
            try:
                rel_type = RelationshipType(rel_type_str)
            except ValueError:
                rel_type = RelationshipType.RELATES_TO
            result = await self.create_relationship(
                rel["source_id"],
                rel["target_id"],
                rel_type,
                rel.get("properties"),
            )
            results.append(result)
        return results

    async def get_relationship_path(self, source_id: str, target_id: str) -> list[list[dict[str, Any]]]:
        await asyncio.sleep(0.01)
        paths: list[list[dict[str, Any]]] = []
        queue: deque[tuple[str, list[dict[str, Any]]]] = deque()
        queue.append((source_id, []))
        visited: set[str] = set()

        while queue and len(paths) < 5:
            current, path = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            for neighbor, rel_type in self._graph.get(current, []):
                new_path = path + [{
                    "source": current,
                    "target": neighbor,
                    "type": rel_type.value,
                }]
                if neighbor == target_id:
                    paths.append(new_path)
                else:
                    queue.append((neighbor, new_path))

        return paths

    async def find_related_entities(self, entity_id: str, relationship_type: RelationshipType | None = None) -> list[dict[str, Any]]:
        await asyncio.sleep(0.01)
        related: list[dict[str, Any]] = []
        for rel in self._relationships:
            if rel["source_id"] == entity_id or rel["target_id"] == entity_id:
                if relationship_type is None or rel["type"] == relationship_type.value:
                    related.append(rel)
        return related