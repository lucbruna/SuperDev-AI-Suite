from __future__ import annotations

from typing import Any


class PlannerGraph:
    """Graph representation of plan task dependencies."""

    def __init__(self):
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: list[tuple[str, str]] = []

    def add_node(self, node_id: str, data: dict[str, Any] | None = None) -> None:
        self._nodes[node_id] = data or {}

    def add_edge(self, from_node: str, to_node: str) -> None:
        self._edges.append((from_node, to_node))

    def get_adjacency_list(self) -> dict[str, list[str]]:
        adj: dict[str, list[str]] = {n: [] for n in self._nodes}
        for from_node, to_node in self._edges:
            if from_node in adj:
                adj[from_node].append(to_node)
        return adj

    def topological_sort(self) -> list[str]:
        adj = self.get_adjacency_list()
        visited: set[str] = set()
        result: list[str] = []

        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for neighbor in adj.get(node, []):
                dfs(neighbor)
            result.append(node)

        for node in self._nodes:
            dfs(node)
        return list(reversed(result))
