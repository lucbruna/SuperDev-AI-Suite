from __future__ import annotations

import json
from typing import Any, Dict, List

from .graph_node import GraphNode
from .graph_edge import GraphEdge


class GraphSerializer:
    """Serializes knowledge graph to/from JSON."""

    @staticmethod
    def serialize(nodes: List[GraphNode], edges: List[GraphEdge]) -> str:
        data = {
            "nodes": [n.to_dict() for n in nodes],
            "edges": [e.to_dict() for e in edges],
        }
        return json.dumps(data, default=str)

    @staticmethod
    def deserialize(data: str) -> Dict[str, Any]:
        return json.loads(data)

    @staticmethod
    def node_to_dict(node: GraphNode) -> Dict[str, Any]:
        return node.to_dict()

    @staticmethod
    def edge_to_dict(edge: GraphEdge) -> Dict[str, Any]:
        return edge.to_dict()
