from __future__ import annotations

import logging
from typing import Any

from .graph import KnowledgeGraph


class GraphTraversal:
    """Breadth-first and depth-first traversal utilities."""

    def __init__(self, graph: KnowledgeGraph | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.knowledge_graph.graph_traversal")
        self.graph = graph or KnowledgeGraph()

    def bfs(self, start: str) -> list[str]:
        visited: list[str] = []
        queue: list[str] = [start]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.append(current)
            queue.extend(neighbor for neighbor in self.graph.neighbors(current) if neighbor not in visited)
        return visited

    def dfs(self, start: str) -> list[str]:
        visited: list[str] = []
        stack: list[str] = [start]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.append(current)
            stack.extend(neighbor for neighbor in reversed(self.graph.neighbors(current)) if neighbor not in visited)
        return visited
