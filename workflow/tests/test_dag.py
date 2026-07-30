from __future__ import annotations

import pytest

from workflow.dag.graph import Graph
from workflow.dag.topological_sort import TopologicalSorter
from workflow.dag.parallel_execution import ParallelExecutor


class TestDag:
    def test_graph_add_node(self) -> None:
        g = Graph()
        g.add_node("a")
        assert g.get_node("a") is not None

    def test_graph_add_edge(self) -> None:
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        e = g.add_edge("a", "b")
        assert e.source == "a"
        assert e.target == "b"

    def test_topological_sort(self) -> None:
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        g.add_node("c")
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        order = TopologicalSorter.sort(g)
        assert order == ["a", "b", "c"]

    def test_topological_sort_cycle(self) -> None:
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        with pytest.raises(ValueError, match="cycle"):
            TopologicalSorter.sort(g)

    def test_parallel_partition(self) -> None:
        g = Graph()
        g.add_node("a")
        g.add_node("b")
        g.add_node("c")
        g.add_edge("a", "c")
        g.add_edge("b", "c")
        order = TopologicalSorter.sort(g)
        levels = ParallelExecutor.partition(g, order)
        assert ["a", "b"] in levels
        assert ["c"] in levels
