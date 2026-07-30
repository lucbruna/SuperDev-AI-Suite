from __future__ import annotations

from typing import Any, Dict


class GraphNode:
    """A node in the knowledge graph."""

    def __init__(self, node_id: str, label: str, properties: Dict[str, Any] | None = None) -> None:
        self._node_id = node_id
        self._label = label
        self._properties = properties or {}

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def label(self) -> str:
        return self._label

    @property
    def properties(self) -> Dict[str, Any]:
        return dict(self._properties)

    def get_property(self, key: str) -> Any:
        return self._properties.get(key)

    def set_property(self, key: str, value: Any) -> None:
        self._properties[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self._node_id,
            "label": self._label,
            "properties": dict(self._properties),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphNode":
        return cls(data["node_id"], data["label"], data.get("properties", {}))
