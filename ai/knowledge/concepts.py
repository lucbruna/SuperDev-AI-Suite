from __future__ import annotations

from typing import Any


class Concept:
    """A knowledge concept with attributes and type information."""

    def __init__(
        self,
        name: str,
        concept_type: str = "",
        description: str = "",
        attributes: dict[str, Any] | None = None,
    ):
        self._name = name
        self._type = concept_type
        self._description = description
        self._attributes = attributes or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def concept_type(self) -> str:
        return self._type

    @property
    def description(self) -> str:
        return self._description

    @property
    def attributes(self) -> dict[str, Any]:
        return dict(self._attributes)

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self._attributes.get(key, default)

    def set_attribute(self, key: str, value: Any) -> None:
        self._attributes[key] = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "type": self._type,
            "description": self._description,
            "attributes": dict(self._attributes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Concept:
        return cls(
            name=data["name"],
            concept_type=data.get("type", ""),
            description=data.get("description", ""),
            attributes=data.get("attributes"),
        )

    def __repr__(self) -> str:
        return f"Concept(name={self._name!r}, type={self._type!r})"
