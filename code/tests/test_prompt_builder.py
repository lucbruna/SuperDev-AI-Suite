from __future__ import annotations

from SuperDev.code.understanding.context_builder import ContextBuilder
from SuperDev.code.understanding.dependency_graph import DependencyGraph
from SuperDev.code.understanding.prompt_builder import PromptBuilder


class TestPromptBuilder:
    def test_build_without_context(self) -> None:
        prompt = PromptBuilder().build("Refactor this")
        assert prompt == "Refactor this"

    def test_build_injects_file_blocks(self) -> None:
        prompt = PromptBuilder().build(
            "Explain",
            [{"path": "a.py", "content": "x = 1\n"}],
        )
        assert "Explain" in prompt
        assert "### FILE: a.py" in prompt
        assert "x = 1" in prompt

    def test_build_multiple_files(self) -> None:
        prompt = PromptBuilder().build(
            "Task",
            [{"path": "a.py", "content": "a"},
             {"path": "b.py", "content": "b"}],
        )
        assert prompt.count("### FILE:") == 2

    def test_build_from_selection(self) -> None:
        graph = DependencyGraph()
        graph.add("a", "b")
        selection = ContextBuilder(max_depth=1).build(["a"], graph)["selected"]
        files = {"a": "print('a')", "b": "print('b')"}
        prompt = PromptBuilder().build_from_selection("Fix", selection, files)
        assert "### FILE: a" in prompt
        assert "print('a')" in prompt
        assert "### FILE: b" in prompt

    def test_tokens_estimate(self) -> None:
        builder = PromptBuilder()
        assert builder.tokens("abcd") == 1
        assert builder.tokens("") >= 1

    def test_fits_budget(self) -> None:
        builder = PromptBuilder(max_tokens=10)
        assert builder.fits_budget("short") is True
        assert builder.fits_budget("x" * 100) is False
