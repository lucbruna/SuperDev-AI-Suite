from __future__ import annotations

import logging
from typing import Any

from .graph import Graph
from .topological_sort import TopologicalSorter
from .parallel_execution import ParallelExecutor


class DagEngine:
    """Engine for executing Directed Acyclic Graphs."""

    def __init__(self) -> None:
        self._graphs: dict[str, Graph] = {}
        self._sorter = TopologicalSorter()
        self._parallel = ParallelExecutor()
        self._log = logging.getLogger("superdev.workflow.dag.engine")

    def register_graph(self, graph_id: str, graph: Graph) -> None:
        self._graphs[graph_id] = graph

    def get_execution_order(self, graph_id: str) -> list[str]:
        graph = self._graphs.get(graph_id)
        if not graph:
            return []
        return self._sorter.sort(graph)

    def get_parallel_levels(self, graph_id: str) -> list[list[str]]:
        graph = self._graphs.get(graph_id)
        if not graph:
            return []
        order = self._sorter.sort(graph)
        return self._parallel.partition(graph, order)

    def validate(self, graph_id: str) -> list[str]:
        graph = self._graphs.get(graph_id)
        if not graph:
            return ["Graph not found"]
        return graph.validate()
