from __future__ import annotations

from typing import Any


class DecisionGraph:
    """Graph-based decision structure with weighted edges."""

    def __init__(self):
        self._nodes: dict[str, dict[str, float]] = {}

    def add_node(self, name: str) -> None:
        if name not in self._nodes:
            self._nodes[name] = {}

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        self.add_node(source)
        self.add_node(target)
        self._nodes[source][target] = weight

    def get_edges(self, node: str) -> dict[str, float]:
        return self._nodes.get(node, {})

    def find_path(self, start: str, end: str) -> list[str]:
        visited: set[str] = set()
        path: list[str] = []

        def dfs(current: str) -> bool:
            if current == end:
                path.append(current)
                return True
            if current in visited:
                return False
            visited.add(current)
            for neighbor in self._nodes.get(current, {}):
                if dfs(neighbor):
                    path.insert(0, current)
                    return True
            return False

        dfs(start)
        return path

    def evaluate(self, start: str) -> dict[str, float]:
        scores: dict[str, float] = {start: 1.0}
        for node in self._nodes:
            for neighbor, weight in self._nodes.get(node, {}).items():
                scores[neighbor] = scores.get(node, 0) * weight
        return scores
