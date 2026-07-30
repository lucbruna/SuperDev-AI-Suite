from __future__ import annotations

from typing import Any, Dict, List, Optional

from .graph_node import GraphNode


class GraphIndex:
    """Index for efficient node lookups."""

    def __init__(self) -> None:
        self._label_index: Dict[str, List[str]] = {}
        self._property_index: Dict[str, Dict[Any, List[str]]] = {}

    def add_node(self, node: GraphNode) -> None:
        label = node.label
        if label not in self._label_index:
            self._label_index[label] = []
        self._label_index[label].append(node.node_id)

        for key, value in node.properties.items():
            if key not in self._property_index:
                self._property_index[key] = {}
            if value not in self._property_index[key]:
                self._property_index[key][value] = []
            self._property_index[key][value].append(node.node_id)

    def remove_node(self, node: GraphNode) -> None:
        label = node.label
        if label in self._label_index:
            self._label_index[label] = [n for n in self._label_index[label] if n != node.node_id]
        for key in node.properties:
            if key in self._property_index:
                for val in list(self._property_index[key]):
                    self._property_index[key][val] = [n for n in self._property_index[key][val] if n != node.node_id]

    def find_by_label(self, label: str) -> List[str]:
        return list(self._label_index.get(label, []))

    def find_by_property(self, key: str, value: Any) -> List[str]:
        return list(self._property_index.get(key, {}).get(value, []))

    def clear(self) -> None:
        self._label_index.clear()
        self._property_index.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "labels": dict(self._label_index),
            "properties": {k: {str(vv): ids for vv, ids in v.items()} for k, v in self._property_index.items()},
        }
