from __future__ import annotations

from collections import deque

from .graph import Graph


class TopologicalSorter:
    """Kahn's algorithm for topological sorting of DAG."""

    @staticmethod
    def sort(graph: Graph) -> list[str]:
        in_degree: dict[str, int] = {
            nid: 0 for nid in graph._nodes
        }
        for edge in graph._edges:
            in_degree[edge.target] = in_degree.get(edge.target, 0) + 1

        queue = deque(
            nid for nid, deg in in_degree.items() if deg == 0
        )
        result: list[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for child in graph.get_children(node):
                in_degree[child.id] -= 1
                if in_degree[child.id] == 0:
                    queue.append(child.id)

        if len(result) != len(graph._nodes):
            raise ValueError("Graph contains a cycle")
        return result
