from __future__ import annotations

import hashlib
from typing import Any

from .quality_models import TestSeverity, VulnerabilityFinding


class QualitySecurity:
    """Security manager for the Testing & Quality Engine.

    Handles finding classification, severity aggregation and audit logging
    for the security test subsystem.
    """

    def __init__(self) -> None:
        self._audit_log: list[dict[str, Any]] = []
        self._policies: dict[str, Any] = {}

    # -- severity helpers ----------------------------------------------------

    @staticmethod
    def severity_rank(severity: TestSeverity) -> int:
        return {
            TestSeverity.LOW: 1,
            TestSeverity.MEDIUM: 2,
            TestSeverity.HIGH: 3,
            TestSeverity.CRITICAL: 4,
        }.get(severity, 0)

    def aggregate(self, findings: list[VulnerabilityFinding]) -> dict[str, Any]:
        """Summarize a list of findings by severity and target."""
        if not findings:
            return {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0, "blocked": False}
        by_severity: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for finding in findings:
            by_severity[finding.severity.value] = by_severity.get(finding.severity.value, 0) + 1
        critical = by_severity["critical"]
        high = by_severity["high"]
        return {
            "total": len(findings),
            "critical": critical,
            "high": high,
            "medium": by_severity["medium"],
            "low": by_severity["low"],
            "blocked": critical > 0 or high > 2,
        }

    def security_score(self, findings: list[VulnerabilityFinding]) -> float:
        """0.0 (many critical) → 1.0 (clean)."""
        if not findings:
            return 1.0
        penalty = sum(
            {TestSeverity.LOW: 0.05, TestSeverity.MEDIUM: 0.1,
             TestSeverity.HIGH: 0.2, TestSeverity.CRITICAL: 0.35}.get(f.severity, 0.1)
            for f in findings
        )
        return round(max(0.0, min(1.0, 1 - penalty)), 4)

    # -- finding helpers -----------------------------------------------------

    @staticmethod
    def checksum(payload: str) -> str:
        return hashlib.sha256(payload.encode()).hexdigest()

    # -- policies ------------------------------------------------------------

    def set_policy(self, name: str, policy: Any) -> None:
        self._policies[name] = policy

    def get_policy(self, name: str) -> Any:
        return self._policies.get(name)

    def evaluate_policy(self, name: str, findings: list[VulnerabilityFinding]) -> bool:
        """A policy passes when no critical findings exist for it."""
        policy = self._policies.get(name)
        if policy is None:
            return True
        blocked = self.aggregate(findings)["blocked"]
        return not blocked

    # -- audit ---------------------------------------------------------------

    def audit(self, action: str, actor: str, details: dict[str, Any] | None = None) -> None:
        self._audit_log.append({
            "action": action,
            "actor": actor,
            "details": details or {},
        })

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._audit_log[-limit:]


__all__ = ["QualitySecurity"]
