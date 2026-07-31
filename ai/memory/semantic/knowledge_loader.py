from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .concepts import Concept
from .entities import Entity
from .relationships import Relationship


class KnowledgeLoader:
    """Loads and imports knowledge from external sources."""

    def load_concepts(self, path: str | Path) -> list[Concept]:
        path = Path(path)
        if not path.exists():
            return []
        raw = path.read_text()
        data = json.loads(raw) if raw.startswith("{") else raw
        if isinstance(data, list):
            return [Concept.from_dict(item) if isinstance(item, dict) else Concept(str(item)) for item in data]
        if isinstance(data, dict):
            return [Concept.from_dict(v) if isinstance(v, dict) else Concept(k) for k, v in data.items()]
        return []

    def load_entities(self, path: str | Path) -> list[Entity]:
        path = Path(path)
        if not path.exists():
            return []
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return [Entity.from_dict(item) for item in data if isinstance(item, dict)]
        return []

    def load_relationships(self, path: str | Path) -> list[Relationship]:
        path = Path(path)
        if not path.exists():
            return []
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return [Relationship(**item) for item in data if isinstance(item, dict)]
        return []

    def load_from_dict(self, data: dict[str, Any]) -> dict[str, list[Any]]:
        result: dict[str, list[Any]] = {"concepts": [], "entities": [], "relationships": []}
        for item in data.get("concepts", []):
            result["concepts"].append(Concept.from_dict(item) if isinstance(item, dict) else Concept(str(item)))
        for item in data.get("entities", []):
            if isinstance(item, dict):
                result["entities"].append(Entity.from_dict(item))
        for item in data.get("relationships", []):
            if isinstance(item, dict):
                result["relationships"].append(Relationship(**item))
        return result
