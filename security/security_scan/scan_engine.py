"""Security scan subsystem (Volume 16) — run all checks and score risk."""

from __future__ import annotations

import asyncio
from typing import Any

from ..base import SecurityReport, Severity
from ..security_models import SecurityScanResult

_SEVERITY_WEIGHTS = {
    Severity.CRITICAL.value: 10.0,
    Severity.HIGH.value: 5.0,
    Severity.MEDIUM.value: 2.0,
    Severity.LOW.value: 1.0,
    Severity.INFO.value: 0.5,
}


class SecurityScanEngine:
    """Aggregate scanner that runs analyzers and produces a risk score."""

    name = "security_scan"
    description = "Aggregated security scan with risk scoring"

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._scans: dict[str, SecurityScanResult] = {}

    @staticmethod
    def risk_score_from_findings(severity_counts: dict[str, int]) -> float:
        total = sum(severity_counts.values())
        if total == 0:
            return 0.0
        weighted = sum(
            count * _SEVERITY_WEIGHTS.get(sev, 1.0)
            for sev, count in severity_counts.items()
        )
        return round(min(100.0, weighted / total * 2), 2)

    def aggregate(self, target: str, reports: list[SecurityReport | dict[str, Any]]) -> SecurityScanResult:
        """Aggregate multiple reports into one scored scan result."""
        findings: list[dict[str, Any]] = []
        for report in reports:
            if hasattr(report, "findings"):
                findings.extend(f.to_dict() for f in report.findings)
            elif isinstance(report, dict):
                findings.extend(report.get("findings", []))
        counts = {sev: 0 for sev in _SEVERITY_WEIGHTS}
        for finding in findings:
            severity = finding.get("severity", "info")
            counts[severity] = counts.get(severity, 0) + 1

        result = SecurityScanResult(
            target=target,
            reports=[r.to_dict() if hasattr(r, "to_dict") else r for r in reports],
            total_findings=len(findings),
            critical_count=counts.get(Severity.CRITICAL.value, 0),
            high_count=counts.get(Severity.HIGH.value, 0),
            medium_count=counts.get(Severity.MEDIUM.value, 0),
            low_count=counts.get(Severity.LOW.value, 0),
            risk_score=self.risk_score_from_findings(counts),
        )
        self._scans[target] = result
        if self.engine is not None:
            self.engine.registry.register_scan(target, result)
            self.engine.metrics.gauge(
                "security.risk_score", result.risk_score, labels={"target": target}
            )
        return result

    async def scan(self, target: str) -> SecurityScanResult:
        """Run every analyzer in the engine and aggregate the results."""
        reports: list[SecurityReport | dict[str, Any]] = []
        for name, subsystem in self.engine.subsystems().items():
            analyzer = getattr(subsystem, "analyze", None)
            if analyzer is None or name == "security_scan":
                continue
            try:
                report = analyzer(target)
                if asyncio.iscoroutine(report):
                    report = await report
                reports.append(report)
            except Exception as exc:  # noqa: BLE001 - aggregate failures
                reports.append({"error": str(exc), "target": target})
        return self.aggregate(target, reports)

    def get(self, target: str) -> SecurityScanResult | None:
        return self._scans.get(target)

    def status(self) -> dict[str, Any]:
        return {"scans": len(self._scans)}
