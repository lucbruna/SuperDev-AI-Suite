from __future__ import annotations

from typing import Any

from .graph import Graph
from .topological_sort import TopologicalSorter
from .parallel_execution import ParallelExecutor


class DagOptimizer:
    """Optimizes DAG execution order and parallelism."""

    @staticmethod
    def optimize(graph: Graph) -> list[list[str]]:
        order = TopologicalSorter.sort(graph)
        return ParallelExecutor.partition(graph, order)

    @staticmethod
    def critical_path(graph: Graph) -> list[str]:
        order = TopologicalSorter.sort(graph)
        longest_path: list[str] = []
        longest_weight = 0.0

        def dfs(node_id: str, path: list[str], weight: float) -> None:
            nonlocal longest_path, longest_weight
            path = path + [node_id]
            node = graph.get_node(node_id)
            weight += node.weight if node else 0
            children = graph.get_children(node_id)
            if not children and weight > longest_weight:
                longest_path = path
                longest_weight = weight
            for child in children:
                dfs(child.id, path, weight)

        for node_id in order:
            if not graph.get_parents(node_id):
                dfs(node_id, [], 0.0)

        return longest_path
