from __future__ import annotations

from typing import Any, Dict, List, Optional


class Entity:
    """A named entity with properties and type information."""

    def __init__(
        self,
        entity_id: str,
        name: str,
        entity_type: str = "unknown",
        properties: Dict[str, Any] | None = None,
    ):
        self._entity_id = entity_id
        self._name = name
        self._type = entity_type
        self._properties = properties or {}

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def entity_type(self) -> str:
        return self._type

    @property
    def properties(self) -> Dict[str, Any]:
        return dict(self._properties)

    def get_property(self, key: str, default: Any = None) -> Any:
        return self._properties.get(key, default)

    def set_property(self, key: str, value: Any) -> None:
        self._properties[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self._entity_id,
            "name": self._name,
            "type": self._type,
            "properties": dict(self._properties),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Entity:
        return cls(
            entity_id=data["entity_id"],
            name=data["name"],
            entity_type=data.get("type", "unknown"),
            properties=data.get("properties"),
        )
