from __future__ import annotations

from typing import Any, Dict, List

from .graph_node import GraphNode
from .graph_edge import GraphEdge


class GraphStatistics:
    """Computes statistics about the knowledge graph."""

    def compute(self, nodes: List[GraphNode], edges: List[GraphEdge]) -> Dict[str, Any]:
        label_counts: Dict[str, int] = {}
        relation_counts: Dict[str, int] = {}

        for node in nodes:
            label_counts[node.label] = label_counts.get(node.label, 0) + 1

        for edge in edges:
            relation_counts[edge.relation] = relation_counts.get(edge.relation, 0) + 1

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "labels": label_counts,
            "relations": relation_counts,
            "avg_edges_per_node": round(len(edges) / max(len(nodes), 1), 2),
        }
