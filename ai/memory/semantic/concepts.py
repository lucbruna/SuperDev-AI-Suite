from __future__ import annotations

from typing import Any


class Concept:
    """A semantic concept representing a unit of knowledge."""

    def __init__(
        self,
        name: str,
        definition: str = "",
        concept_type: str = "general",
        attributes: dict[str, Any] | None = None,
    ):
        self._name = name
        self._definition = definition
        self._type = concept_type
        self._attributes = attributes or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def definition(self) -> str:
        return self._definition

    @property
    def concept_type(self) -> str:
        return self._type

    @property
    def attributes(self) -> dict[str, Any]:
        return dict(self._attributes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "definition": self._definition,
            "type": self._type,
            "attributes": dict(self._attributes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Concept:
        return cls(
            name=data["name"],
            definition=data.get("definition", ""),
            concept_type=data.get("type", "general"),
            attributes=data.get("attributes"),
        )
