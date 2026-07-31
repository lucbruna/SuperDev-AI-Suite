"""Knowledge connections."""

from __future__ import annotations

import time
from typing import Any


class KnowledgeConnection:
    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: list[dict[str, Any]] = []

    def add_node(
        self, node_id: str, content: str, node_type: str = "concept", metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        node = {
            "id": node_id,
            "content": content,
            "type": node_type,
            "metadata": metadata or {},
            "created_at": time.time(),
        }
        self._nodes[node_id] = node
        return node

    def add_edge(self, source: str, target: str, relation: str = "related_to", weight: float = 1.0) -> dict[str, Any]:
        edge = {"source": source, "target": target, "relation": relation, "weight": weight, "created_at": time.time()}
        self._edges.append(edge)
        return edge

    def get_neighbors(self, node_id: str) -> list[dict[str, Any]]:
        neighbors = []
        for e in self._edges:
            if e["source"] == node_id:
                neighbors.append(
                    {"node": self._nodes.get(e["target"], {}), "relation": e["relation"], "direction": "outgoing"}
                )
            elif e["target"] == node_id:
                neighbors.append(
                    {"node": self._nodes.get(e["source"], {}), "relation": e["relation"], "direction": "incoming"}
                )
        return neighbors

    def search(self, query: str) -> list[dict[str, Any]]:
        return [n for n in self._nodes.values() if query.lower() in n.get("content", "").lower()]

    def get_node(self, node_id: str) -> dict[str, Any]:
        return self._nodes.get(node_id, {"error": "not_found"})

    def delete_node(self, node_id: str) -> bool:
        if node_id in self._nodes:
            del self._nodes[node_id]
            self._edges = [e for e in self._edges if e["source"] != node_id and e["target"] != node_id]
            return True
        return False

    def list_nodes(self) -> list[str]:
        return list(self._nodes.keys())

    def edge_count(self) -> int:
        return len(self._edges)
