from __future__ import annotations

from typing import Any, Dict, List, Optional

from .graph_node import GraphNode
from .graph_edge import GraphEdge


class KnowledgeGraphEngine:
    """Central knowledge graph orchestrator."""

    def __init__(self) -> None:
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: List[GraphEdge] = []

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    @property
    def node_ids(self) -> List[str]:
        return list(self._nodes.keys())

    def add_node(self, node: GraphNode) -> None:
        self._nodes[node.node_id] = node

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)

    def remove_node(self, node_id: str) -> bool:
        if node_id in self._nodes:
            del self._nodes[node_id]
            self._edges = [e for e in self._edges if e.source != node_id and e.target != node_id]
            return True
        return False

    def add_edge(self, edge: GraphEdge) -> None:
        self._edges.append(edge)

    def get_edges(self, node_id: Optional[str] = None) -> List[GraphEdge]:
        if node_id is None:
            return list(self._edges)
        return [e for e in self._edges if e.source == node_id or e.target == node_id]

    def remove_edge(self, edge_id: str) -> bool:
        for i, e in enumerate(self._edges):
            if e.edge_id == edge_id:
                del self._edges[i]
                return True
        return False

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges],
        }
