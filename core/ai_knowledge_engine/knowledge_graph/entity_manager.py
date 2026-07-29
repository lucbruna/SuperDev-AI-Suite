from __future__ import annotations

import asyncio
from typing import Any

EntityRegistry = dict[str, dict[str, Any]]


class EntityManager:
    def __init__(self) -> None:
        self._entities: EntityRegistry = {}

    async def create_entity(self, entity_id: str, label: str, properties: dict[str, Any] | None = None) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        if entity_id in self._entities:
            raise ValueError(f"Entity already exists: {entity_id}")
        entity = {
            "id": entity_id,
            "label": label,
            "properties": properties or {},
        }
        self._entities[entity_id] = entity
        return entity

    async def update_entity(self, entity_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        if entity_id not in self._entities:
            raise ValueError(f"Entity not found: {entity_id}")
        self._entities[entity_id]["properties"].update(properties)
        return self._entities[entity_id]

    async def delete_entity(self, entity_id: str) -> bool:
        await asyncio.sleep(0.01)
        if entity_id not in self._entities:
            return False
        del self._entities[entity_id]
        return True

    async def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        await asyncio.sleep(0.01)
        return self._entities.get(entity_id)

    async def find_entity(self, query: str) -> list[dict[str, Any]]:
        await asyncio.sleep(0.01)
        query_lower = query.lower()
        results: list[dict[str, Any]] = []
        for entity in self._entities.values():
            if (query_lower in entity["id"].lower()
                    or query_lower in entity["label"].lower()
                    or any(query_lower in str(v).lower() for v in entity["properties"].values())):
                results.append(entity)
        return results

    async def list_entities(self, label: str | None = None) -> list[dict[str, Any]]:
        await asyncio.sleep(0.01)
        if label is None:
            return list(self._entities.values())
        return [e for e in self._entities.values() if e["label"] == label]

    async def get_entity_relations(self, entity_id: str, relations: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
        await asyncio.sleep(0.01)
        return relations.get(entity_id, [])