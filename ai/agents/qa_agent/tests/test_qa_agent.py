from __future__ import annotations

from ..acceptance import Acceptance
from ..bug_detector import BugDetector
from ..coverage import Coverage
from ..metrics import Metrics
from ..mutation_testing import MutationTesting
from ..qa_agent import QAAgent
from ..quality_analyzer import QualityAnalyzer
from ..regression import Regression
from ..smoke_tests import SmokeTests


class TestQualityAnalyzer:
    def test_analyze_code(self) -> None:
        qa = QualityAnalyzer()
        results = qa.analyze_code("some code")
        assert len(results) > 0

    def test_add_metric(self) -> None:
        qa = QualityAnalyzer()
        qa.add_metric("complexity", "Cyclomatic complexity", 10.0)
        assert qa.metric_count == 1

    def test_calculate_score(self) -> None:
        qa = QualityAnalyzer()
        score = qa.calculate_score("short code")
        assert score > 0

    def test_to_dict(self) -> None:
        qa = QualityAnalyzer()
        qa.add_metric("m", "desc", 1.0)
        d = qa.to_dict()
        assert "metrics" in d


class TestBugDetector:
    def test_detect_bugs_none_check(self) -> None:
        bd = BugDetector()
        results = bd.detect_bugs("if x == None:")
        assert len(results) > 0

    def test_detect_bugs_bare_except(self) -> None:
        bd = BugDetector()
        results = bd.detect_bugs("try:\n    pass\nexcept:")
        assert any(r["pattern"] == "empty_except" for r in results)

    def test_add_pattern(self) -> None:
        bd = BugDetector()
        bd.add_bug_pattern("custom", "Check for X", "high")
        assert bd.pattern_count > 0

    def test_to_dict(self) -> None:
        bd = BugDetector()
        assert "patterns" in bd.to_dict()


class TestRegression:
    def test_add_test(self) -> None:
        r = Regression()
        r.add_test("test_login", "Login flow test", "integration")
        assert r.test_count == 1

    def test_remove_test(self) -> None:
        r = Regression()
        r.add_test("t", "desc")
        assert r.remove_test("t") is True

    def test_run_suite(self) -> None:
        r = Regression()
        r.add_test("t1", "d")
        r.add_test("t2", "d")
        result = r.run_regression_suite()
        assert "total" in result

    def test_list_by_category(self) -> None:
        r = Regression()
        r.add_test("t", "d", "unit")
        assert len(r.list_tests("unit")) == 1

    def test_to_dict(self) -> None:
        r = Regression()
        r.add_test("t", "d")
        assert "tests" in r.to_dict()


class TestSmokeTests:
    def test_add_smoke_test(self) -> None:
        s = SmokeTests()
        s.add_smoke_test("homepage", "/", 200)
        assert s.test_count == 1

    def test_run_suite(self) -> None:
        s = SmokeTests()
        s.add_smoke_test("h", "/")
        results = s.run_smoke_suite()
        assert len(results) == 1

    def test_to_dict(self) -> None:
        s = SmokeTests()
        s.add_smoke_test("h", "/")
        assert "tests" in s.to_dict()


class TestAcceptance:
    def test_add_criteria(self) -> None:
        a = Acceptance()
        a.add_criteria("C1", "User can login", "functional")
        assert a.criteria_count == 1

    def test_verify(self) -> None:
        a = Acceptance()
        a.add_criteria("C1", "desc")
        results = a.verify(["C1"])
        assert len(results) == 1

    def test_to_dict(self) -> None:
        a = Acceptance()
        a.add_criteria("C", "d")
        assert "criteria" in a.to_dict()


class TestCoverage:
    def test_analyze(self) -> None:
        c = Coverage()
        result = c.analyze("src/module.py")
        assert "line_coverage" in result

    def test_add_target(self) -> None:
        c = Coverage()
        c.add_target("src/core", 80.0)
        assert c.target_count == 1

    def test_suggest_tests(self) -> None:
        c = Coverage()
        suggestions = c.suggest_tests("src/mod.py")
        assert len(suggestions) > 0

    def test_to_dict(self) -> None:
        c = Coverage()
        c.add_target("m", 90.0)
        assert "targets" in c.to_dict()


class TestMutationTesting:
    def test_add_mutant(self) -> None:
        mt = MutationTesting()
        mt.add_mutant("a + b", "a - b", "replace")
        assert mt.mutant_count == 1

    def test_run_suite(self) -> None:
        mt = MutationTesting()
        mt.add_mutant("a", "b")
        result = mt.run_mutation_suite()
        assert "kill_rate" in result

    def test_properties(self) -> None:
        mt = MutationTesting()
        assert mt.survival_rate == 0.0

    def test_to_dict(self) -> None:
        mt = MutationTesting()
        mt.add_mutant("a", "b")
        d = mt.to_dict()
        assert "mutants" in d


class TestMetrics:
    def test_record(self) -> None:
        m = Metrics()
        m.record("test_time", 42.5)
        assert m.metric_count == 1

    def test_summary(self) -> None:
        m = Metrics()
        m.record("latency", 10)
        m.record("latency", 20)
        s = m.summary("latency")
        assert s["avg"] == 15.0

    def test_list_names(self) -> None:
        m = Metrics()
        m.record("a", 1)
        assert "a" in m.list_metric_names()

    def test_generate_dashboard(self) -> None:
        m = Metrics()
        m.record("cpu", 50)
        dash = m.generate_dashboard()
        assert "Dashboard" in dash

    def test_to_dict(self) -> None:
        m = Metrics()
        m.record("m", 1)
        d = m.to_dict()
        assert "metrics" in d


class TestQAAgent:
    def test_engine_initializes(self) -> None:
        qa = QAAgent()
        assert qa.quality is not None
        assert qa.bugs is not None
        assert qa.regression is not None
        assert qa.smoke is not None
        assert qa.acceptance is not None
        assert qa.coverage is not None
        assert qa.mutation is not None
        assert qa.metrics is not None

    def test_run_quality_check(self) -> None:
        qa = QAAgent()
        result = qa.run_quality_check({"code": "def foo():\n    pass"})
        assert result["status"] == "checked"

    def test_get_status(self) -> None:
        qa = QAAgent()
        s = qa.get_status()
        assert "quality_score" in s

    def test_to_dict(self) -> None:
        qa = QAAgent()
        d = qa.to_dict()
        assert d["agent"] == "qa_agent"
