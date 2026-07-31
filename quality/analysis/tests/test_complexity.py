"""Tests for the ComplexityAnalyzer deep-dive module."""

from __future__ import annotations

from SuperDev.quality.analysis import ComplexityAnalyzer


class TestTokenizer:
    def test_comments_and_strings_ignored(self) -> None:
        source = (
            "# if x: this is a comment\n"
            "text = 'if y: not a branch'\n"
            "if z:\n"
            "    pass\n"
        )
        analyzer = ComplexityAnalyzer()
        # Comentário e string descartados — apenas o `if z:` conta.
        assert analyzer.cyclomatic_complexity(source) == 2

    def test_multiline_string_ignored(self) -> None:
        source = '"""\nif inside_docstring:\n    pass\n"""\nvalue = 1\n'
        analyzer = ComplexityAnalyzer()
        assert analyzer.cyclomatic_complexity(source) == 1


class TestMetrics:
    def test_cyclomatic_complexity(self) -> None:
        source = (
            "def f(x):\n"
            "    if x > 0:\n"
            "        return 1\n"
            "    elif x < 0:\n"
            "        return -1\n"
            "    return 0\n"
        )
        analyzer = ComplexityAnalyzer()
        # 1 (base) + if + elif = 3
        assert analyzer.cyclomatic_complexity(source) == 3

    def test_nesting_depth(self) -> None:
        source = (
            "def f():\n"
            "    if a:\n"
            "        for b in c:\n"
            "            while d:\n"
            "                pass\n"
        )
        analyzer = ComplexityAnalyzer()
        # def=0, if=1, for=2, while=3, pass=4 → profundidade máxima 4.
        assert analyzer.nesting_depth(source) == 4

    def test_branch_count(self) -> None:
        source = (
            "if a:\n"
            "    pass\n"
            "for b in c:\n"
            "    pass\n"
            "assert d\n"
        )
        analyzer = ComplexityAnalyzer()
        assert analyzer.branch_count(source) == 3

    def test_function_count(self) -> None:
        source = "def a():\n    pass\n\nasync def b():\n    pass\n"
        analyzer = ComplexityAnalyzer()
        assert analyzer.function_count(source) == 1  # apenas `def ` (não async)


class TestClassification:
    def test_classify_levels(self) -> None:
        assert ComplexityAnalyzer.classify(1) == ("low", 1.0)
        assert ComplexityAnalyzer.classify(8) == ("medium", 0.8)
        assert ComplexityAnalyzer.classify(15) == ("high", 0.6)
        assert ComplexityAnalyzer.classify(50) == ("critical", 0.4)

    def test_analyze_summary(self) -> None:
        analyzer = ComplexityAnalyzer()
        result = analyzer.analyze("if a:\n    pass\n", target="mod")
        assert result["complexity"] == 2
        assert result["risk"] == "low"
        assert result["score"] == 1.0
        assert analyzer.get("mod") is result


class TestEngineWiring:
    def test_wired_in_engine(self, engine) -> None:
        result = engine.analysis.complexity_analyzer.analyze(
            "if a:\n    if b:\n        pass\n", target="wired"
        )
        assert result["complexity"] == 3  # 1 (base) + if + if
        assert result["depth"] == 2
        assert engine.metrics.get_gauge("analysis.complexity", {"target": "wired"}) == 3
        assert engine.metrics.get_counter("analysis.complexity_runs") >= 1
