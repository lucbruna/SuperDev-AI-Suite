from __future__ import annotations

from typing import Any

from .quality_models import (
    CoverageReport,
    PerformanceReport,
    ProductionGate,
    QualityScore,
    TestResult,
    TestSuite,
    VulnerabilityFinding,
)


class QualityRegistry:
    """Registry for the Testing & Quality Engine components."""

    def __init__(self) -> None:
        self._suites: dict[str, TestSuite] = {}
        self._results: dict[str, TestResult] = {}
        self._coverage: dict[str, CoverageReport] = {}
        self._findings: dict[str, VulnerabilityFinding] = {}
        self._performance: dict[str, PerformanceReport] = {}
        self._scores: dict[str, QualityScore] = {}
        self._gates: dict[str, ProductionGate] = {}
        self._rules: dict[str, Any] = {}

    # -- suites --------------------------------------------------------------

    def register_suite(self, suite: TestSuite) -> None:
        self._suites[suite.suite_id] = suite

    def get_suite(self, suite_id: str) -> TestSuite | None:
        return self._suites.get(suite_id)

    def list_suites(self) -> dict[str, TestSuite]:
        return dict(self._suites)

    # -- results -------------------------------------------------------------

    def register_result(self, result: TestResult) -> None:
        self._results[result.result_id] = result

    def get_result(self, result_id: str) -> TestResult | None:
        return self._results.get(result_id)

    def list_results(self) -> dict[str, TestResult]:
        return dict(self._results)

    # -- coverage ------------------------------------------------------------

    def register_coverage(self, report: CoverageReport) -> None:
        self._coverage[report.report_id] = report

    def get_coverage(self, report_id: str) -> CoverageReport | None:
        return self._coverage.get(report_id)

    # -- findings ------------------------------------------------------------

    def register_finding(self, finding: VulnerabilityFinding) -> None:
        self._findings[finding.finding_id] = finding

    def get_finding(self, finding_id: str) -> VulnerabilityFinding | None:
        return self._findings.get(finding_id)

    def list_findings(self) -> dict[str, VulnerabilityFinding]:
        return dict(self._findings)

    # -- performance ---------------------------------------------------------

    def register_performance(self, report: PerformanceReport) -> None:
        self._performance[report.report_id] = report

    def get_performance(self, report_id: str) -> PerformanceReport | None:
        return self._performance.get(report_id)

    # -- scores --------------------------------------------------------------

    def register_score(self, score: QualityScore) -> None:
        self._scores[score.score_id] = score

    def get_score(self, score_id: str) -> QualityScore | None:
        return self._scores.get(score_id)

    def list_scores(self) -> dict[str, QualityScore]:
        return dict(self._scores)

    # -- gates ---------------------------------------------------------------

    def register_gate(self, gate: ProductionGate) -> None:
        self._gates[gate.gate_id] = gate

    def get_gate(self, gate_id: str) -> ProductionGate | None:
        return self._gates.get(gate_id)

    def list_gates(self) -> dict[str, ProductionGate]:
        return dict(self._gates)

    # -- rules ---------------------------------------------------------------

    def register_rule(self, name: str, rule: Any) -> None:
        self._rules[name] = rule

    def get_rule(self, name: str) -> Any:
        return self._rules.get(name)

    def list_rules(self) -> dict[str, Any]:
        return dict(self._rules)

    @property
    def size(self) -> int:
        return (
            len(self._suites)
            + len(self._results)
            + len(self._coverage)
            + len(self._findings)
            + len(self._performance)
            + len(self._scores)
            + len(self._gates)
            + len(self._rules)
        )


__all__ = ["QualityRegistry"]
