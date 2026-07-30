from __future__ import annotations

from typing import Any

from .graph_node import GraphNode
from .graph_edge import GraphEdge


class GraphValidator:
    """Validates graph nodes, edges, and structure."""

    @staticmethod
    def validate_node(node: Any) -> bool:
        return isinstance(node, GraphNode) and bool(node.node_id) and bool(node.label)

    @staticmethod
    def validate_edge(edge: Any) -> bool:
        if not isinstance(edge, GraphEdge):
            return False
        return bool(edge.edge_id) and bool(edge.source) and bool(edge.target) and bool(edge.relation)

    @staticmethod
    def validate_no_duplicate_nodes(nodes: list) -> bool:
        ids = [n.node_id for n in nodes if isinstance(n, GraphNode)]
        return len(ids) == len(set(ids))

    @staticmethod
    def validate_references(edge: GraphEdge, node_ids: set) -> bool:
        return edge.source in node_ids and edge.target in node_ids
