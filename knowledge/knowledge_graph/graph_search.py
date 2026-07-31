from __future__ import annotations

import logging
from collections import deque

from .graph import KnowledgeGraph


class GraphSearch:
    """Traversal and path-finding over the knowledge graph."""

    def __init__(self, graph: KnowledgeGraph | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.knowledge_graph.graph_search")
        self.graph = graph or KnowledgeGraph()

    def connected(self, start: str, target: str) -> bool:
        return len(self.shortest_path(start, target)) > 0

    def shortest_path(self, start: str, target: str) -> list[str]:
        if start == target:
            return [start]
        queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
        visited = {start}
        while queue:
            current, path = queue.popleft()
            for neighbor in self.graph.neighbors(current):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                next_path = path + [neighbor]
                if neighbor == target:
                    return next_path
                queue.append((neighbor, next_path))
        return []

    def reachable(self, start: str, depth: int = 1) -> list[str]:
        frontier = {start}
        for _ in range(max(0, depth)):
            frontier = {neighbor for node in frontier for neighbor in self.graph.neighbors(node)}
        return sorted(frontier)

    def expand(self, start: str) -> list[str]:
        return self.reachable(start, depth=1)
