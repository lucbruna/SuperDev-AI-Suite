from __future__ import annotations

from collections import defaultdict

from .graph import Graph
from .topological_sort import TopologicalSorter


class ParallelExecutor:
    """Partitions DAG into parallel execution levels."""

    @staticmethod
    def partition(graph: Graph, order: list[str]) -> list[list[str]]:
        levels: list[list[str]] = []
        level_of: dict[str, int] = {}
        for node_id in order:
            parents = [
                e.source for e in graph._edges if e.target == node_id
            ]
            if not parents:
                level_of[node_id] = 0
            else:
                level_of[node_id] = max(level_of[p] for p in parents) + 1

        by_level: dict[int, list[str]] = defaultdict(list)
        for nid, lvl in level_of.items():
            by_level[lvl].append(nid)

        for lvl in sorted(by_level.keys()):
            levels.append(by_level[lvl])
        return levels

    @staticmethod
    def max_parallelism(graph: Graph) -> int:
        order = TopologicalSorter.sort(graph)
        levels = ParallelExecutor.partition(graph, order)
        return max(len(l) for l in levels) if levels else 0
