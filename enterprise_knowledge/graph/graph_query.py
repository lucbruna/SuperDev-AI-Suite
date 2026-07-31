"""Graph queries: paths, reachability, connected components and traversal."""

from __future__ import annotations

from collections import deque
from typing import Any


class GraphQuery:
    """BFS/DFS traversal helpers over the knowledge graph."""

    def __init__(self, neighbors_fn: Any = None) -> None:
        # neighbors_fn(node_id) -> list[dict] with "node_id" entries
        self._neighbors_fn = neighbors_fn

    def _neighbors(self, node_id: str) -> list[str]:
        if self._neighbors_fn is None:
            return []
        return [n["node_id"] for n in self._neighbors_fn(node_id)]

    def neighbors_of(self, node_id: str) -> list[str]:
        return self._neighbors(node_id)

    def reachable(self, start: str, limit: int = 100) -> list[str]:
        """All nodes reachable from ``start`` (BFS, excluding itself)."""
        visited: set[str] = set()
        queue = deque([start])
        while queue and len(visited) < limit:
            current = queue.popleft()
            for neighbor in self._neighbors(current):
                if neighbor not in visited and neighbor != start:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return list(visited)

    def shortest_path(self, start: str, target: str) -> list[str]:
        """Shortest path between two nodes (BFS); empty if unreachable."""
        if start == target:
            return [start]
        queue: deque[list[str]] = deque([[start]])
        visited = {start}
        while queue:
            path = queue.popleft()
            last = path[-1]
            for neighbor in self._neighbors(last):
                if neighbor in visited:
                    continue
                new_path = path + [neighbor]
                if neighbor == target:
                    return new_path
                visited.add(neighbor)
                queue.append(new_path)
        return []

    def path_exists(self, start: str, target: str) -> bool:
        return bool(self.shortest_path(start, target))

    def degrees(self, node_ids: list[str]) -> dict[str, int]:
        return {node_id: len(self._neighbors(node_id))
                for node_id in node_ids}

    def most_connected(self, node_ids: list[str],
                       limit: int = 5) -> list[tuple[str, int]]:
        ranked = sorted(self.degrees(node_ids).items(),
                        key=lambda item: item[1], reverse=True)
        return ranked[:max(0, limit)]

    def connected_components(self, node_ids: list[str]) -> list[list[str]]:
        remaining = set(node_ids)
        components: list[list[str]] = []
        while remaining:
            start = next(iter(remaining))
            component = self.reachable(start)
            component.append(start)
            for node_id in component:
                remaining.discard(node_id)
            components.append(component)
        return components
