from __future__ import annotations

from typing import Any


class Relationship:
    """A formal relationship in the semantic model."""

    def __init__(
        self,
        name: str,
        source_type: str,
        target_type: str,
        description: str = "",
        properties: dict[str, Any] | None = None,
    ):
        self._name = name
        self._source_type = source_type
        self._target_type = target_type
        self._description = description
        self._properties = properties or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def source_type(self) -> str:
        return self._source_type

    @property
    def target_type(self) -> str:
        return self._target_type

    @property
    def description(self) -> str:
        return self._description

    @property
    def properties(self) -> dict[str, Any]:
        return dict(self._properties)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "source_type": self._source_type,
            "target_type": self._target_type,
            "description": self._description,
            "properties": dict(self._properties),
        }
