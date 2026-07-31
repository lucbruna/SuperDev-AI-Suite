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


class TestPromptTruncation:
    """Tests for per-file token truncation in the middle of FILE blocks."""

    @staticmethod
    def _make_file(n_lines: int) -> str:
        return "\n".join(f"def fn_{i}(arg): return {i}" for i in range(n_lines))

    def test_disabled_by_default(self) -> None:
        builder = PromptBuilder()
        content = self._make_file(200)
        prompt = builder.build("T", [{"path": "big.py", "content": content}])
        assert "def fn_0" in prompt and "def fn_199" in prompt
        assert builder.last_truncated == []

    def test_short_file_untouched(self) -> None:
        builder = PromptBuilder(max_file_tokens=50)
        prompt = builder.build("T", [{"path": "small.py", "content": "x = 1\n"}])
        assert "x = 1" in prompt
        assert "truncated" not in prompt
        assert builder.last_truncated == []

    def test_long_file_truncated_in_middle(self) -> None:
        builder = PromptBuilder(max_file_tokens=40)
        content = self._make_file(100)
        prompt = builder.build("T", [{"path": "big.py", "content": content}])
        # head and tail are kept (where imports/trailing defs live)...
        assert "def fn_0" in prompt
        assert "def fn_99" in prompt
        # ...the middle is replaced by a marker line.
        assert "truncated" in prompt and "lines" in prompt
        assert "def fn_50" not in prompt
        # the file was recorded as truncated and the prompt shrank
        assert builder.last_truncated == ["big.py"]
        assert builder.tokens(prompt) < builder.tokens(
            PromptBuilder().build("T", [{"path": "big.py",
                                          "content": content}]))

    def test_single_huge_line_falls_back_to_slicing(self) -> None:
        builder = PromptBuilder(max_file_tokens=10)
        content = """

""" + "z" * 2000
        prompt = builder.build("T", [{"path": "huge.py", "content": content}])
        assert "zzzz" in prompt          # slice of the giant line survives
        assert "truncated" in prompt
        assert builder.last_truncated == ["huge.py"]

    def test_truncated_prompt_fits_tight_budget(self) -> None:
        builder = PromptBuilder(max_tokens=300, max_file_tokens=40)
        content = self._make_file(200)
        prompt = builder.build("T", [{"path": "big.py", "content": content}])
        assert builder.fits_budget(prompt) is True
        assert builder.last_truncated == ["big.py"]

    def test_build_from_selection_truncates(self) -> None:
        graph = DependencyGraph()
        graph.add("a", "b")
        selection = ContextBuilder(max_depth=1).build(["a"], graph)["selected"]
        files = {"a": self._make_file(200), "b": "print('b')"}
        builder = PromptBuilder(max_file_tokens=40)
        prompt = builder.build_from_selection("Fix", selection, files)
        assert "truncated" in prompt
        assert builder.last_truncated == ["a"]


class TestPromptGlobalBudget:
    """Tests for the global ``max_tokens`` pass in ``PromptBuilder.build``.

    Independent of ``max_file_tokens``, the whole prompt must fit
    ``max_tokens``: trailing files (least relevant, since the selection is
    ranked) are truncated further in the middle until the budget fits and,
    when even a minimal slice cannot fit, dropped entirely (tracked in
    ``last_dropped``).
    """

    @staticmethod
    def _make_file(n_lines: int) -> str:
        return "\n".join(f"def fn_{i}(arg): return {i}" for i in range(n_lines))

    def test_global_budget_truncates_trailing_file_in_middle(self) -> None:
        builder = PromptBuilder(max_tokens=150)  # no max_file_tokens
        big = self._make_file(200)
        prompt = builder.build("T", [{"path": "a.py", "content": "x = 1\n"},
                                     {"path": "big.py", "content": big}])
        # the whole prompt fits the global budget...
        assert builder.fits_budget(prompt) is True
        # ...by truncating the trailing (least relevant) file in the middle,
        # not by dropping it.
        assert builder.last_truncated == ["big.py"]
        assert builder.last_dropped == []
        assert "### FILE: big.py" in prompt
        assert "def fn_0" in prompt and "def fn_199" in prompt
        # either the line-based marker ("lines") or the char-slice fallback
        # ("truncated") may be used depending on the exact estimates
        assert "truncated" in prompt

    def test_global_budget_drops_file_when_minimal_slice_cannot_fit(self) -> None:
        builder = PromptBuilder(max_tokens=30)
        big = self._make_file(200)
        prompt = builder.build("T", [{"path": "big1.py", "content": big},
                                     {"path": "big2.py", "content": big}])
        assert builder.fits_budget(prompt) is True
        # big1 survives (truncated to a minimal slice); big2 cannot even
        # fit that slice — the tail file is dropped and recorded.
        assert "### FILE: big1.py" in prompt
        assert "### FILE: big2.py" not in prompt
        assert builder.last_dropped == ["big2.py"]
        assert builder.last_truncated == ["big1.py"]

    def test_global_budget_drops_trailing_files_until_prompt_fits(self) -> None:
        builder = PromptBuilder(max_tokens=40)
        big = self._make_file(200)
        prompt = builder.build("T", [{"path": "big1.py", "content": big},
                                     {"path": "big2.py", "content": big},
                                     {"path": "big3.py", "content": big}])
        assert builder.fits_budget(prompt) is True
        # least relevant first: big3 then big2 dropped, head of the ranked
        # selection (big1) kept.
        assert builder.last_dropped == ["big3.py", "big2.py"]
        assert "### FILE: big1.py" in prompt
        assert all(p not in prompt for p in builder.last_dropped)

    def test_global_budget_keeps_seed_head_when_dropping(self) -> None:
        """The head of the ranked selection (seed, most relevant) always
        survives; only trailing files are sacrificed to the budget."""
        builder = PromptBuilder(max_tokens=25)
        big = self._make_file(200)
        prompt = builder.build("T", [{"path": "seed.py", "content": big},
                                     {"path": "dep.py", "content": big}])
        assert builder.fits_budget(prompt) is True
        assert "### FILE: seed.py" in prompt
        assert builder.last_dropped == ["dep.py"]

    def test_truncation_and_drop_tracking_reset_per_build(self) -> None:
        builder = PromptBuilder(max_tokens=30)
        big = self._make_file(200)
        builder.build("T", [{"path": "a.py", "content": big},
                            {"path": "b.py", "content": big}])
        assert builder.last_dropped == ["b.py"]
        # a fresh build resets both trackers.
        prompt = builder.build("T", [{"path": "small.py", "content": "x\n"}])
        assert builder.last_truncated == []
        assert builder.last_dropped == []
        assert "### FILE: small.py" in prompt

    def test_global_budget_respects_larger_budget(self) -> None:
        """With a generous budget the global pass is a no-op: no truncation
        and no drops happen even with multiple large files."""
        builder = PromptBuilder(max_tokens=10_000)
        big = self._make_file(100)
        prompt = builder.build("T", [{"path": f"f{i}.py", "content": big}
                                     for i in range(4)])
        assert builder.fits_budget(prompt) is True
        assert builder.last_truncated == []
        assert builder.last_dropped == []
        assert prompt.count("### FILE:") == 4
