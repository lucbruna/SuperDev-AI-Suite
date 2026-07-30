from __future__ import annotations

from typing import Dict, List, Optional, Set

from .graph_node import GraphNode
from .graph_edge import GraphEdge


class GraphTraversal:
    """Traversal strategies for the knowledge graph."""

    def __init__(self) -> None:
        self._visited: Set[str] = set()

    def bfs(self, start_id: str, nodes: Dict[str, GraphNode], edges: List[GraphEdge]) -> List[GraphNode]:
        self._visited.clear()
        queue = [start_id]
        result: List[GraphNode] = []
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

    def dfs(self, start_id: str, nodes: Dict[str, GraphNode], edges: List[GraphEdge]) -> List[GraphNode]:
        self._visited.clear()
        result: List[GraphNode] = []
        adj = self._build_adjacency(edges)
        self._dfs_recursive(start_id, nodes, adj, result)
        return result

    def find_path(self, start: str, end: str, edges: List[GraphEdge]) -> List[str]:
        adj = self._build_adjacency(edges)
        queue: List[List[str]] = [[start]]
        visited: Set[str] = {start}
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

    def _build_adjacency(self, edges: List[GraphEdge]) -> Dict[str, List[str]]:
        adj: Dict[str, List[str]] = {}
        for e in edges:
            adj.setdefault(e.source, []).append(e.target)
            adj.setdefault(e.target, []).append(e.source)
        return adj

    def _dfs_recursive(self, current: str, nodes: Dict[str, GraphNode], adj: Dict[str, List[str]], result: List[GraphNode]) -> None:
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
