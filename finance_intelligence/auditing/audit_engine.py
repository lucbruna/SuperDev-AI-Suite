"""Auditing subsystem facade (Volume 35).

Aggregates the immutable audit trail, audit reports and compliance checks.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.auditing.audit_reports import AuditReports
from finance_intelligence.auditing.audit_trail import AuditTrail
from finance_intelligence.auditing.compliance_checks import ComplianceChecks
from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_registry import FinanceRegistry


class AuditEngine:
    """Aggregate facade over the auditing subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.trail = AuditTrail(self.registry, self.events)
        self.reports = AuditReports()
        self.compliance = ComplianceChecks()

    # -- convenience ---------------------------------------------------------
    def record(self, event: str, actor: str = "system",
               target: str = "", detail: dict[str, Any] | None = None,
               created_at: float | None = None):
        return self.trail.record(event, actor, target, detail, created_at)

    def findings(self) -> list[dict[str, Any]]:
        return self.compliance.run(self.registry)

    def is_compliant(self) -> bool:
        return self.compliance.is_compliant(self.registry)

    def status(self) -> str:
        return self.compliance.status(self.registry)

    def stats(self) -> dict[str, Any]:
        audits = self.trail.list()
        return {
            "audits": len(audits),
            "actors": len({audit.actor for audit in audits}),
            "events": len({audit.event for audit in audits}),
            "compliance_status": self.status(),
        }
