from __future__ import annotations

from typing import Any


class GraphSearch:
    """Graph-based search traversing relationships between entries."""

    def __init__(self):
        self._search_count: int = 0

    @property
    def search_count(self) -> int:
        return self._search_count

    def search(self, query: str, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q = query.lower()
        results: list[dict[str, Any]] = []
        for entry in entries:
            content = str(entry.get("content", "")).lower()
            if q in content:
                results.append(entry)
            related = entry.get("related", [])
            if isinstance(related, list):
                for rel in related:
                    if isinstance(rel, dict) and q in str(rel.get("content", "")).lower():
                        results.append(entry)
                        break
        self._search_count += 1
        return results

    def bfs(self, start_id: str, graph: dict[str, list[str]], max_depth: int = 3) -> list[str]:
        visited: set = {start_id}
        queue: list[tuple] = [(start_id, 0)]
        order: list[str] = []
        while queue:
            node, depth = queue.pop(0)
            order.append(node)
            if depth >= max_depth:
                continue
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
        self._search_count += 1
        return order

    def dfs(self, start_id: str, graph: dict[str, list[str]], max_depth: int = 3) -> list[str]:
        visited: set = set()
        order: list[str] = []

        def _dfs(node: str, depth: int) -> None:
            if node in visited or depth > max_depth:
                return
            visited.add(node)
            order.append(node)
            for neighbor in graph.get(node, []):
                _dfs(neighbor, depth + 1)

        _dfs(start_id, 0)
        self._search_count += 1
        return order

    def reset(self) -> None:
        self._search_count = 0
