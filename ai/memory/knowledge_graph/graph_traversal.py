from __future__ import annotations

from .graph_edge import GraphEdge
from .graph_node import GraphNode


class GraphTraversal:
    """Traversal strategies for the knowledge graph."""

    def __init__(self) -> None:
        self._visited: set[str] = set()

    def bfs(self, start_id: str, nodes: dict[str, GraphNode], edges: list[GraphEdge]) -> list[GraphNode]:
        self._visited.clear()
        queue = [start_id]
        result: list[GraphNode] = []
        adj = self._build_adjacency(edges)
        while queue:
            current = queue.pop(0)
            if current in self._visited:
                continue
            self._visited.add(current)
            node = nodes.get(current)
            if node:
                result.append(node)
            for neighbor in adj.get(current, []):
                if neighbor not in self._visited:
                    queue.append(neighbor)
        return result

    def dfs(self, start_id: str, nodes: dict[str, GraphNode], edges: list[GraphEdge]) -> list[GraphNode]:
        self._visited.clear()
        result: list[GraphNode] = []
        adj = self._build_adjacency(edges)
        self._dfs_recursive(start_id, nodes, adj, result)
        return result

    def find_path(self, start: str, end: str, edges: list[GraphEdge]) -> list[str]:
        adj = self._build_adjacency(edges)
        queue: list[list[str]] = [[start]]
        visited: set[str] = {start}
        while queue:
            path = queue.pop(0)
            last = path[-1]
            if last == end:
                return path
            for neighbor in adj.get(last, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(list(path) + [neighbor])
        return []

    def _build_adjacency(self, edges: list[GraphEdge]) -> dict[str, list[str]]:
        adj: dict[str, list[str]] = {}
        for e in edges:
            adj.setdefault(e.source, []).append(e.target)
            adj.setdefault(e.target, []).append(e.source)
        return adj

    def _dfs_recursive(self, current: str, nodes: dict[str, GraphNode], adj: dict[str, list[str]], result: list[GraphNode]) -> None:
        if current in self._visited:
            return
        self._visited.add(current)
        node = nodes.get(current)
        if node:
            result.append(node)
        for neighbor in adj.get(current, []):
            self._dfs_recursive(neighbor, nodes, adj, result)

    @property
    def visited_count(self) -> int:
        return len(self._visited)

    def reset(self) -> None:
        self._visited.clear()
