from __future__ import annotations

from pathlib import Path

import pytest

from SuperDev.quality.quality_engine import QualityEngine
from SuperDev.quality.quality_models import TestCase, TestKind, TestSuite


class TestTesting:
    @pytest.mark.asyncio
    async def test_run_suite(self, engine: QualityEngine) -> None:
        suite = TestSuite(name="demo", target="mod")
        suite.cases = [
            TestCase(name="passes", assertions=[True]),
            TestCase(name="fails", assertions=[False]),
            TestCase(name="empty", assertions=[]),
        ]
        engine.testing.register_suite(suite)
        result = await engine.testing.run_suite(suite)
        assert result.total == 3
        assert result.passed == 2
        assert result.failed == 1
        assert result.status.value == "failed"

    @pytest.mark.asyncio
    async def test_run_case(self, engine: QualityEngine) -> None:
        case = TestCase(name="single", assertions=[1 == 1])
        result = await engine.testing.run_case(case)
        assert result.status.value == "passed"
        assert engine.metrics.get_counter("testing.cases", {"status": "passed"}) >= 1

    def test_schedule(self, engine: QualityEngine) -> None:
        suite = TestSuite(name="s")
        engine.testing.register_suite(suite)
        assert engine.testing.schedule(suite.suite_id, at=0.0) is True
        assert engine.testing.due_suites(now=1.0) == [suite.suite_id]


class TestUnit:
    def test_generate_suite(self, engine: QualityEngine) -> None:
        suite = engine.unit.generate_suite("calc", source="def total():\n    return 1\n")
        assert len(suite.cases) >= 3
        assert suite.kind == TestKind.UNIT

    def test_mocking(self, engine: QualityEngine) -> None:
        mock = engine.unit.create_mock("db", returns=42)
        assert engine.unit.call_mock("db", 1) == 42
        assert engine.unit.verify_called("db", times=1)
        assert mock["calls"] == 1

    def test_assertions(self, engine: QualityEngine) -> None:
        assert engine.unit.assert_equals(1, 1)
        assert engine.unit.assert_in("a", "abc")
        assert engine.unit.assert_raises(lambda: 1 / 0, ZeroDivisionError)

    def test_coverage_target(self, engine: QualityEngine) -> None:
        assert engine.unit.meets_target(0.85)
        assert not engine.unit.meets_target(0.5)


class TestIntegration:
    def test_categories(self, engine: QualityEngine) -> None:
        suite = engine.integration.create_suite("full", category="api", target="svc")
        assert engine.integration.add_api_test(suite.suite_id, "/users", 200)
        assert engine.integration.add_database_test(suite.suite_id, "SELECT 1", 1)
        assert engine.integration.add_workflow_test(suite.suite_id, "onboarding", 3)
        assert engine.integration.add_agent_test(suite.suite_id, "coder", "completed")
        assert engine.integration.add_deployment_test(suite.suite_id, "staging")
        assert len(suite.cases) == 5

    def test_invalid_category(self, engine: QualityEngine) -> None:
        with pytest.raises(ValueError):
            engine.integration.create_suite("bad", category="nope")


class TestRegression:
    def test_baseline_and_changes(self, engine: QualityEngine) -> None:
        assert not engine.regression.has_baseline("api")
        assert engine.regression.detect_changes("api", {"latency": 10}) == [
            {"key": "baseline", "change": "created"}
        ]
        changes = engine.regression.detect_changes("api", {"latency": 30})
        assert len(changes) == 1
        assert changes[0]["severity"] == "high"

    def test_compare_regression(self, engine: QualityEngine) -> None:
        engine.regression.set_baseline("api", {"errors": 0})
        comparison = engine.regression.compare("api", {"errors": 5})
        assert comparison["regression"] is True
        assert comparison["high_impact"] >= 1


class TestPerformance:
    def test_latency(self, engine: QualityEngine) -> None:
        stats = engine.performance.latency(lambda: None, samples=20)
        assert stats["samples"] == 20
        assert stats["avg_ms"] >= 0

    def test_throughput(self, engine: QualityEngine) -> None:
        rate = engine.performance.throughput(lambda: None, duration_s=0.1)
        assert rate > 0

    def test_load_and_stress(self, engine: QualityEngine) -> None:
        load = engine.performance.load_test(lambda: None, users=5, samples=10)
        assert load["users"] == 5
        stress = engine.performance.stress_test(lambda: None, iterations=50)
        assert stress["iterations"] == 50
        assert stress["failure_rate"] == 0.0

    def test_report_and_score(self, engine: QualityEngine) -> None:
        report = engine.performance.build_report("svc", {
            "avg_latency_ms": 5.0, "p95_latency_ms": 10.0,
            "throughput": 500.0, "error_rate": 0.0,
        })
        assert engine.performance.performance_score(report) == 1.0


class TestSecurity:
    def test_vulnerability_scan(self, engine: QualityEngine) -> None:
        findings = engine.security.vulnerability_scan("mod", "result = eval(user_input)")
        assert any("eval" in f.title for f in findings)

    def test_clean_scan(self, engine: QualityEngine) -> None:
        findings = engine.security.vulnerability_scan("mod", "result = 1 + 1")
        assert findings == []
        assert engine.metrics.get_counter("security.scans_clean") >= 1

    def test_dependency_scan(self, engine: QualityEngine) -> None:
        low = engine.security.scan_dependency("requests", "2.31.0")
        assert low["risk"] == "low"
        high = engine.security.scan_dependency("deprecated-lib", "1.0.0")
        assert high["risk"] == "high"

    def test_auth_and_api(self, engine: QualityEngine) -> None:
        result = engine.security.authentication_test({"password": "short", "authenticated": True})
        assert result["weak_password"] is True
        assert engine.security.authorization_test({"admin": {"deploy"}}, "deploy", "admin")
        assert not engine.security.authorization_test({"admin": {"deploy"}}, "delete", "admin")
        scan = engine.security.api_security_scan(["/api/v1/admin/users", "/api/v1/public"])
        assert scan["sensitive_exposed"] == 1


class TestAutomation:
    def test_generation(self, engine: QualityEngine) -> None:
        cases = engine.automation.generate_tests("mod")
        assert len(cases) == 3
        suite = engine.automation.generate_suite("mod2")
        assert suite.suite_id

    def test_partition(self, engine: QualityEngine) -> None:
        cases = [TestCase(name=f"c{i}") for i in range(9)]
        batches = engine.automation.partition(cases, workers=4)
        assert len(batches) == 4
        assert sum(len(b) for b in batches) == 9

    def test_retry_and_notify(self, engine: QualityEngine) -> None:
        assert engine.automation.should_retry("c1", max_retries=2)
        assert engine.automation.should_retry("c1", max_retries=2)
        assert not engine.automation.should_retry("c1", max_retries=2)
        engine.automation.notify("slack", "Tests done")
        assert len(engine.automation.recent_notifications()) == 1


class TestCoverage:
    def test_measure(self, engine: QualityEngine) -> None:
        report = engine.coverage.measure("mod", {
            "covered_lines": 80, "total_lines": 100,
            "covered_branches": 50, "total_branches": 100,
            "covered_functions": 9, "total_functions": 10,
        })
        assert report.line == 0.8
        assert report.branch == 0.5
        assert report.function == 0.9

    def test_targets(self, engine: QualityEngine) -> None:
        report = engine.coverage.measure("mod", {"covered_lines": 90, "total_lines": 100})
        assert engine.coverage.meets_targets(report)


class TestAnalysis:
    def test_complexity(self, engine: QualityEngine) -> None:
        source = "def f():\n    if a:\n        for i in b:\n            while c:\n                pass\n"
        result = engine.analysis.complexity(source)
        assert result["complexity"] >= 4

    def test_duplication(self, engine: QualityEngine) -> None:
        assert engine.analysis.duplication("a = 1\na = 1\na = 1") > 0.5
        assert engine.analysis.duplication("x = 1\ny = 2") == 0.0

    def test_analyze_code(self, engine: QualityEngine) -> None:
        analysis = engine.analysis.analyze_code("mod", '"""doc"""\ndef f(x: int) -> int:\n    return x\n')
        assert analysis["quality"] > 0.5

    def test_score(self, engine: QualityEngine) -> None:
        score = engine.analysis.score("app", code=0.9, tests=0.8)
        assert score.overall == pytest.approx(0.85, abs=0.001)


class TestBenchmarking:
    def test_benchmark(self, engine: QualityEngine) -> None:
        engine.benchmarking.register_suite("s", {"a": lambda: None, "b": lambda: None})
        results = engine.benchmarking.run("s", iterations=5)
        assert set(results) == {"a", "b"}

    def test_compare_and_rank(self, engine: QualityEngine) -> None:
        engine.benchmarking.register_suite("s", {"fast": lambda: None, "slow": lambda: 1 / 0})
        engine.benchmarking.run("s", iterations=3)
        comparison = engine.benchmarking.compare("s", "fast", "slow")
        assert comparison["available"] is True
        assert comparison["winner"] == "fast"
        assert engine.benchmarking.rank_operations("s")[0]["op"] == "fast"


class TestReports:
    @pytest.mark.asyncio
    async def test_test_report(self, engine: QualityEngine) -> None:
        from SuperDev.quality.quality_models import TestResult

        result = TestResult(total=4, passed=4, status="passed")
        report_id = await engine.reports.create_test_report("mod", result)
        rendered = engine.reports.render(report_id)
        assert "Test Report: mod" in rendered
        assert "Passed: 4" in rendered

    @pytest.mark.asyncio
    async def test_executive_report(self, engine: QualityEngine) -> None:
        report_id = await engine.reports.create_executive_report("app", {
            "decision": "approved", "quality_score": 0.95, "checks": [1, 2],
        })
        rendered = engine.reports.render(report_id)
        assert "APPROVED" in rendered
        assert "95.0%" in rendered

    @pytest.mark.asyncio
    async def test_export(self, engine: QualityEngine, tmp_path) -> None:
        score = engine.compute_score("app", code=0.9, tests=0.9)
        report_id = await engine.reports.create_quality_report("app", score)
        path = str(tmp_path / "report.md")
        assert engine.reports.export_markdown(report_id, path)
        with Path(path).open(encoding="utf-8") as handle:
            assert "Quality Report: app" in handle.read()


class TestValidation:
    @pytest.mark.asyncio
    async def test_rules(self, engine: QualityEngine) -> None:
        engine.validation.register_rule("coverage_gte", {
            "field": "coverage", "op": "gte", "value": 0.75,
        })
        assert engine.validation.check_rule("coverage_gte", {"coverage": 0.8})
        assert not engine.validation.check_rule("coverage_gte", {"coverage": 0.5})

    @pytest.mark.asyncio
    async def test_policy(self, engine: QualityEngine) -> None:
        engine.validation.register_rule("cov", {"field": "coverage", "op": "min_pct", "value": 0.7})
        engine.validation.set_policy("release", ["cov"])
        result = engine.validation.evaluate_policy("release", {"coverage": 0.9})
        assert result["passed"] is True

    def test_approval(self, engine: QualityEngine) -> None:
        engine.validation.require_approval("app", approver="alice")
        assert not engine.validation.is_approved("app")
        assert engine.validation.approve("app", "alice")
        assert engine.validation.is_approved("app")

    @pytest.mark.asyncio
    async def test_gate(self, engine: QualityEngine) -> None:
        gate = await engine.validation.evaluate_gate("app", {
            "quality_score": 0.95, "coverage": 0.9, "tests_passed": True,
        })
        assert gate.decision.value == "approved"
        assert engine.validation.list_gates()

    def test_compliance(self, engine: QualityEngine) -> None:
        engine.validation.set_policy("gdpr", [])
        report = engine.validation.compliance_report("app")
        assert report["compliant"] is True
