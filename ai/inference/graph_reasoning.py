from __future__ import annotations

from typing import Any


class GraphReasoning:
    """Graph-based relational reasoning."""

    def __init__(self) -> None:
        self._graph: dict[str, list[str]] = {}

    def add_edge(self, source: str, target: str) -> None:
        if source not in self._graph:
            self._graph[source] = []
        self._graph[source].append(target)

    async def traverse(self, start: str, strategy: str = "bfs") -> list[str]:
        if strategy == "bfs":
            return await self._bfs(start)
        return await self._dfs(start)

    async def _bfs(self, start: str) -> list[str]:
        visited: list[str] = []
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node not in visited:
                visited.append(node)
                queue.extend(self._graph.get(node, []))
        return visited

    async def _dfs(self, start: str) -> list[str]:
        visited: list[str] = []
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.append(node)
                stack.extend(self._graph.get(node, []))
        return visited

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        start = context.get("start", "")
        strategy = context.get("strategy", "bfs")
        path = await self.traverse(start, strategy)
        return {"path": path, "nodes_visited": len(path)}
