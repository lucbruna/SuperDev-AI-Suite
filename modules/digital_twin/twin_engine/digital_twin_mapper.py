"""Twin model builder: normalizes raw reality into canonical entities."""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.config.constants import ENTITY_TYPES


class TwinMapperError(ValueError):
    """Raised when raw data cannot be mapped to a twin entity."""


@dataclass(slots=True)
class MappedEntity:
    """A normalized entity inside the twin."""

    id: str
    type: str
    name: str
    properties: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "properties": dict(self.properties),
        }


class TwinMapper:
    """Maps raw reality records into canonical twin entities."""

    def __init__(self, allowed_types: tuple[str, ...] = ENTITY_TYPES) -> None:
        self._allowed = allowed_types

    def map(self, raw: dict[str, object]) -> MappedEntity:
        entity_id = raw.get("id")
        entity_type = raw.get("type")
        name = raw.get("name", "")
        if not entity_id or not entity_type:
            raise TwinMapperError("raw record requires 'id' and 'type'")
        if entity_type not in self._allowed:
            raise TwinMapperError(f"unsupported entity type: {entity_type}")
        properties = {
            k: v for k, v in raw.items() if k not in {"id", "type", "name"}
        }
        return MappedEntity(
            id=str(entity_id),
            type=str(entity_type),
            name=str(name),
            properties=properties,
        )

    def map_many(self, raws: list[dict[str, object]]) -> list[MappedEntity]:
        return [self.map(raw) for raw in raws]
