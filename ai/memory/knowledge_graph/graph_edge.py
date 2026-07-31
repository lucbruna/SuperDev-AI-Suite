from __future__ import annotations

from typing import Any


class GraphEdge:
    """A directed edge in the knowledge graph."""

    def __init__(self, edge_id: str, source: str, target: str, relation: str, properties: dict[str, Any] | None = None) -> None:
        self._edge_id = edge_id
        self._source = source
        self._target = target
        self._relation = relation
        self._properties = properties or {}

    @property
    def edge_id(self) -> str:
        return self._edge_id

    @property
    def source(self) -> str:
        return self._source

    @property
    def target(self) -> str:
        return self._target

    @property
    def relation(self) -> str:
        return self._relation

    @property
    def properties(self) -> dict[str, Any]:
        return dict(self._properties)

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self._edge_id,
            "source": self._source,
            "target": self._target,
            "relation": self._relation,
            "properties": dict(self._properties),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphEdge:
        return cls(
            data["edge_id"],
            data["source"],
            data["target"],
            data["relation"],
            data.get("properties", {}),
        )
