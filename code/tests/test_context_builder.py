from __future__ import annotations

from SuperDev.code.understanding.context_builder import (
    ContextBuilder,
    estimate_tokens,
)
from SuperDev.code.understanding.dependency_graph import DependencyGraph


def make_graph() -> DependencyGraph:
    graph = DependencyGraph()
    # a -> b, a -> c, c -> d ; e -> a (dependent edge into the seed)
    graph.add("a", "b")
    graph.add("a", "c")
    graph.add("c", "d")
    graph.add("e", "a")
    return graph


class TestEstimateTokens:
    def test_non_zero(self) -> None:
        assert estimate_tokens("") == 1
        assert estimate_tokens("x" * 100) == 25


class TestContextBuilder:
    def test_seed_files_always_included_first(self) -> None:
        graph = make_graph()
        result = ContextBuilder().build(["a"], graph)
        assert result["files"][0] == "a"

    def test_multiple_seeds(self) -> None:
        graph = make_graph()
        result = ContextBuilder(max_depth=0).build(["a", "e"], graph)
        assert result["files"] == ["a", "e"]

    def test_bfs_follows_dependencies(self) -> None:
        graph = make_graph()
        result = ContextBuilder(max_depth=1).build(["a"], graph)
        assert result["files"][0] == "a"
        assert "b" in result["files"]
        assert "c" in result["files"]
        assert "d" not in result["files"]  # depth 2

    def test_bfs_respects_max_depth(self) -> None:
        graph = make_graph()
        result = ContextBuilder(max_depth=2).build(["a"], graph)
        assert "d" in result["files"]

    def test_bfs_includes_dependents(self) -> None:
        graph = make_graph()
        result = ContextBuilder(max_depth=1).build(["a"], graph)
        assert "e" in result["files"]  # e depends on a -> pulled in

    def test_max_files_budget(self) -> None:
        graph = make_graph()
        result = ContextBuilder(max_files=2).build(["a"], graph)
        assert len(result["files"]) == 2

    def test_max_tokens_budget_drops_non_seed_files(self) -> None:
        graph = make_graph()
        files = {"a": "x" * 400, "b": "y" * 400, "c": "z" * 400,
                 "e": "w" * 400}
        # Seed 'a' (~100 tokens) is always kept; the other files (~100
        # tokens each) exceed the remaining budget, including dependent 'e'.
        result = ContextBuilder(max_tokens=150).build(["a"], graph, files)
        assert result["files"] == ["a"]

    def test_depth_metadata(self) -> None:
        graph = make_graph()
        result = ContextBuilder(max_depth=2).build(["a"], graph)
        by_path = {entry["path"]: entry["depth"] for entry in result["selected"]}
        assert by_path["a"] == 0
        assert by_path["b"] == 1
        assert by_path["d"] == 2

    def test_returns_budget_summary(self) -> None:
        graph = make_graph()
        result = ContextBuilder(max_files=5, max_tokens=500).build(["a"], graph)
        assert result["budget"] == {"max_files": 5, "max_tokens": 500}
        assert result["total_tokens"] >= 0
