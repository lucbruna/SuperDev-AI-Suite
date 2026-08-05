"""FailureDetector: runs all health checks and aggregates failures."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aios.self_healing.health_check import HealthCheck, HealthStatus


@dataclass
class FailureReport:
    failing: list[str] = field(default_factory=list)
    critical: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    statuses: list[HealthStatus] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failing

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "failing": list(self.failing),
            "critical": list(self.critical),
            "warnings": list(self.warnings),
            "statuses": [status.to_dict() for status in self.statuses],
        }


class FailureDetector:
    """Runs registered checks in name order; deterministic failure reporting."""

    def __init__(self) -> None:
        self._checks: dict[str, HealthCheck] = {}

    def register(self, check: HealthCheck) -> bool:
        if check.name in self._checks:
            raise KeyError(f"health check {check.name!r} already registered")
        self._checks[check.name] = check
        return True

    def check_names(self) -> list[str]:
        return sorted(self._checks)

    def run_all(self) -> FailureReport:
        statuses = [self._checks[name].run() for name in self.check_names()]
        report = FailureReport(statuses=statuses)
        for status in statuses:
            if status.ok:
                continue
            report.failing.append(status.name)
            if status.critical:
                report.critical.append(status.name)
            else:
                report.warnings.append(status.name)
        report.failing.sort()
        report.critical.sort()
        report.warnings.sort()
        return report
