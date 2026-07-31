from __future__ import annotations

from pathlib import Path
from typing import Any

from ..quality_models import (
    PerformanceReport,
    TestResult,
    VulnerabilityFinding,
)


class QualityReportEngine:
    """Quality reports — test, quality, security, performance, executive, export."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.reports
        self._reports: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- builders ------------------------------------------------------------

    async def create_test_report(self, target: str, result: TestResult) -> str:
        report = {
            "kind": "test",
            "target": target,
            "result": result,
            "rendered": self.render_test(target, result),
        }
        return self._store(report)

    async def create_quality_report(
        self,
        target: str,
        score: dict[str, Any],
        result: TestResult | None = None,
    ) -> str:
        report = {
            "kind": "quality",
            "target": target,
            "score": score,
            "result": result,
            "rendered": self.render_quality(target, score, result),
        }
        return self._store(report)

    async def create_security_report(
        self,
        target: str,
        findings: list[VulnerabilityFinding],
    ) -> str:
        report = {
            "kind": "security",
            "target": target,
            "findings": findings,
            "rendered": self.render_security(target, findings),
        }
        return self._store(report)

    async def create_performance_report(
        self,
        target: str,
        performance: PerformanceReport,
    ) -> str:
        report = {
            "kind": "performance",
            "target": target,
            "performance": performance,
            "rendered": self.render_performance(target, performance),
        }
        return self._store(report)

    async def create_executive_report(self, target: str, signals: dict[str, Any]) -> str:
        report = {
            "kind": "executive",
            "target": target,
            "signals": signals,
            "rendered": self.render_executive(target, signals),
        }
        return self._store(report)

    def _store(self, report: dict[str, Any]) -> str:
        report_id = f"report-{len(self._reports) + 1}"
        self._reports[report_id] = report
        self.engine.metrics.increment("reports.generated", labels={"kind": report["kind"]})
        return report_id

    # -- renderers -----------------------------------------------------------

    def render_test(self, target: str, result: TestResult) -> str:
        return (
            f"# Test Report: {target}\n\n"
            f"- Status: **{result.status.value}**\n"
            f"- Total: {result.total} | Passed: {result.passed} | "
            f"Failed: {result.failed} | Skipped: {result.skipped} | Errors: {result.errors}\n"
            f"- Pass rate: {result.passed_rate:.1%}\n"
            f"- Duration: {result.duration_ms:.1f} ms\n"
        )

    def render_quality(
        self,
        target: str,
        score: dict[str, Any],
        result: TestResult | None = None,
    ) -> str:
        lines = [
            f"# Quality Report: {target}",
            "",
            "## Quality Score",
            f"- Code: {score.get('code', 0):.1%}",
            f"- Tests: {score.get('tests', 0):.1%}",
            f"- Security: {score.get('security', 0):.1%}",
            f"- Performance: {score.get('performance', 0):.1%}",
            f"- Documentation: {score.get('documentation', 0):.1%}",
            f"- **Overall: {score.get('overall', 0):.1%}**",
        ]
        if result is not None:
            lines.append("")
            lines.append("## Test Results")
            lines.append(f"- Passed: {result.passed}/{result.total}")
        return "\n".join(lines)

    def render_security(self, target: str, findings: list[VulnerabilityFinding]) -> str:
        lines = [f"# Security Report: {target}", ""]
        if not findings:
            lines.append("No findings. ✅")
            return "\n".join(lines)
        lines.append(f"Findings: {len(findings)}")
        lines.append("")
        for finding in findings:
            lines.append(
                f"- **[{finding.severity.value.upper()}]** {finding.title} — {finding.location}"
            )
        return "\n".join(lines)

    def render_performance(self, target: str, performance: PerformanceReport) -> str:
        return (
            f"# Performance Report: {target}\n\n"
            f"- Avg latency: {performance.avg_latency_ms:.1f} ms\n"
            f"- P95 latency: {performance.p95_latency_ms:.1f} ms\n"
            f"- Throughput: {performance.throughput:.1f} ops/s\n"
            f"- Error rate: {performance.error_rate:.2%}\n"
            f"- Peak memory: {performance.peak_memory_mb:.1f} MB\n"
        )

    def render_executive(self, target: str, signals: dict[str, Any]) -> str:
        decision = signals.get("decision", "unknown")
        score = signals.get("quality_score", 0.0)
        checks = signals.get("checks", [])
        blocked = signals.get("blocked_reasons", [])
        lines = [
            f"# Executive Quality Report: {target}",
            "",
            f"- **Decision: {decision.upper()}**",
            f"- Quality score: {score:.1%}",
            f"- Checks: {len(checks)}",
        ]
        if blocked:
            lines.append("")
            lines.append("## Blocked reasons")
            for reason in blocked:
                lines.append(f"- {reason}")
        return "\n".join(lines)

    # -- accessors -----------------------------------------------------------

    def render(self, report_id: str) -> str:
        report = self._reports.get(report_id)
        if report is None:
            return ""
        return report.get("rendered", "")

    def get(self, report_id: str) -> dict[str, Any] | None:
        return self._reports.get(report_id)

    def list_reports(self) -> list[dict[str, Any]]:
        return list(self._reports.values())

    def export_markdown(self, report_id: str, path: str) -> bool:
        rendered = self.render(report_id)
        if not rendered:
            return False
        with Path(path).open("w", encoding="utf-8") as handle:
            handle.write(rendered)
        return True

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "reports": len(self._reports),
        }


__all__ = ["QualityReportEngine"]
