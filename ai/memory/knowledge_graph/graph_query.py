from __future__ import annotations

from typing import Any, Dict, List, Optional

from .graph_node import GraphNode
from .graph_edge import GraphEdge


class GraphQuery:
    """Query builder for the knowledge graph."""

    def __init__(self) -> None:
        self._label_filter: Optional[str] = None
        self._property_filters: Dict[str, Any] = {}
        self._relation_filter: Optional[str] = None
        self._limit: Optional[int] = None

    def filter_by_label(self, label: str) -> "GraphQuery":
        self._label_filter = label
        return self

    def filter_by_property(self, key: str, value: Any) -> "GraphQuery":
        self._property_filters[key] = value
        return self

    def filter_by_relation(self, relation: str) -> "GraphQuery":
        self._relation_filter = relation
        return self

    def limit(self, count: int) -> "GraphQuery":
        self._limit = count
        return self

    def execute_nodes(self, nodes: List[GraphNode]) -> List[GraphNode]:
        results = list(nodes)
        if self._label_filter:
            results = [n for n in results if n.label == self._label_filter]
        for k, v in self._property_filters.items():
            results = [n for n in results if n.get_property(k) == v]
        if self._limit:
            results = results[: self._limit]
        return results

    def execute_edges(self, edges: List[GraphEdge]) -> List[GraphEdge]:
        results = list(edges)
        if self._relation_filter:
            results = [e for e in results if e.relation == self._relation_filter]
        if self._limit:
            results = results[: self._limit]
        return results

    def reset(self) -> None:
        self._label_filter = None
        self._property_filters.clear()
        self._relation_filter = None
        self._limit = None
