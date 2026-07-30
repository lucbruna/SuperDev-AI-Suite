from __future__ import annotations

from collections import defaultdict
from typing import Any


class PlannerDAG:
    """Directed Acyclic Graph for plan task dependencies."""

    def __init__(self):
        self._nodes: dict[str, dict[str, Any]] = {}
        self._in_edges: dict[str, list[str]] = defaultdict(list)
        self._out_edges: dict[str, list[str]] = defaultdict(list)

    def add_node(self, node_id: str, data: dict[str, Any] | None = None) -> None:
        self._nodes[node_id] = data or {}

    def add_dependency(self, from_node: str, to_node: str) -> None:
        self._out_edges[from_node].append(to_node)
        self._in_edges[to_node].append(from_node)

    def get_dependencies(self, node_id: str) -> list[str]:
        return list(self._in_edges.get(node_id, []))

    def get_dependents(self, node_id: str) -> list[str]:
        return list(self._out_edges.get(node_id, []))

    def is_acyclic(self) -> bool:
        visited: set[str] = set()
        path: set[str] = set()

        def dfs(node: str) -> bool:
            if node in path:
                return False
            if node in visited:
                return True
            visited.add(node)
            path.add(node)
            for neighbor in self._out_edges.get(node, []):
                if not dfs(neighbor):
                    return False
            path.remove(node)
            return True

        for node in self._nodes:
            if node not in visited:
                if not dfs(node):
                    return False
        return True

    def execution_order(self) -> list[str]:
        visited: set[str] = set()
        result: list[str] = []

        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in self._in_edges.get(node, []):
                dfs(dep)
            result.append(node)

        for node in self._nodes:
            dfs(node)
        return result
