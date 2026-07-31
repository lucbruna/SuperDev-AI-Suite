"""Data lineage tracking."""

from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Any


class DataLineage:
    """Tracks how datasets derive from one another."""

    def __init__(self) -> None:
        self.edges: list[dict[str, Any]] = []

    def add_edge(self, source: str, target: str,
                 operation: str = "derived") -> None:
        self.edges.append({"source": source, "target": target,
                           "operation": operation,
                           "ts": datetime.now().isoformat()})

    def upstream(self, dataset: str) -> set[str]:
        """All datasets the given dataset depends on (recursively)."""
        found: set[str] = set()
        frontier = [dataset]
        while frontier:
            current = frontier.pop()
            for edge in self.edges:
                if edge["target"] == current and edge["source"] not in found:
                    found.add(edge["source"])
                    frontier.append(edge["source"])
        return found

    def downstream(self, dataset: str) -> set[str]:
        """All datasets derived from the given one (recursively)."""
        found: set[str] = set()
        frontier = [dataset]
        while frontier:
            current = frontier.pop()
            for edge in self.edges:
                if edge["source"] == current and edge["target"] not in found:
                    found.add(edge["target"])
                    frontier.append(edge["target"])
        return found

    def impact(self, dataset: str) -> dict[str, Any]:
        """Impact analysis: what breaks if the dataset changes."""
        affected = self.downstream(dataset)
        return {"dataset": dataset, "affected": sorted(affected),
                "count": len(affected)}

    def path(self, source: str, target: str) -> list[str]:
        """Shortest chain of datasets from source to target (BFS)."""
        if source == target:
            return [source]
        visited = {source}
        frontier = deque([(source, [source])])
        while frontier:
            current, route = frontier.popleft()
            for edge in self.edges:
                nxt = edge["target"]
                if edge["source"] == current and nxt not in visited:
                    new_route = route + [nxt]
                    if nxt == target:
                        return new_route
                    visited.add(nxt)
                    frontier.append((nxt, new_route))
        return []

    def stats(self) -> dict[str, Any]:
        nodes = {edge["source"] for edge in self.edges} | \
            {edge["target"] for edge in self.edges}
        return {"edges": len(self.edges), "datasets": sorted(nodes)}
