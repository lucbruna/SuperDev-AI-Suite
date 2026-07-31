from __future__ import annotations

import json
from typing import Any

from .graph_edge import GraphEdge
from .graph_node import GraphNode


class GraphSerializer:
    """Serializes knowledge graph to/from JSON."""

    @staticmethod
    def serialize(nodes: list[GraphNode], edges: list[GraphEdge]) -> str:
        data = {
            "nodes": [n.to_dict() for n in nodes],
            "edges": [e.to_dict() for e in edges],
        }
        return json.dumps(data, default=str)

    @staticmethod
    def deserialize(data: str) -> dict[str, Any]:
        return json.loads(data)

    @staticmethod
    def node_to_dict(node: GraphNode) -> dict[str, Any]:
        return node.to_dict()

    @staticmethod
    def edge_to_dict(edge: GraphEdge) -> dict[str, Any]:
        return edge.to_dict()
