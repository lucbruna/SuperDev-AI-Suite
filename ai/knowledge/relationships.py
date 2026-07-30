from __future__ import annotations

from typing import Any


class Relationship:
    """A typed relationship between two or more concepts."""

    def __init__(
        self,
        name: str,
        source: str,
        target: str,
        rel_type: str = "directed",
        properties: dict[str, Any] | None = None,
    ):
        self._name = name
        self._source = source
        self._target = target
        self._type = rel_type
        self._properties = properties or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def source(self) -> str:
        return self._source

    @property
    def target(self) -> str:
        return self._target

    @property
    def rel_type(self) -> str:
        return self._type

    @property
    def properties(self) -> dict[str, Any]:
        return dict(self._properties)

    def get_property(self, key: str, default: Any = None) -> Any:
        return self._properties.get(key, default)

    def set_property(self, key: str, value: Any) -> None:
        self._properties[key] = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "source": self._source,
            "target": self._target,
            "type": self._type,
            "properties": dict(self._properties),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Relationship:
        return cls(
            name=data["name"],
            source=data["source"],
            target=data["target"],
            rel_type=data.get("type", "directed"),
            properties=data.get("properties"),
        )

    def __repr__(self) -> str:
        return f"Relationship({self._source} --[{self._name}]--> {self._target})"
