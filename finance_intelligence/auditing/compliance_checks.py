"""Compliance checks for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import TransactionStatus
from finance_intelligence.finance_registry import FinanceRegistry


class ComplianceChecks:
    """Run control checks over the registry for compliance posture."""

    def run(self, registry: FinanceRegistry) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        transactions = registry.list_transactions()

        pending = [tx for tx in transactions
                   if tx.status == TransactionStatus.PENDING]
        if pending:
            findings.append({
                "check": "pending_transactions",
                "status": "fail",
                "detail": f"{len(pending)} transaction(s) pending approval",
            })

        open_alerts = registry.open_alerts()
        if open_alerts:
            findings.append({
                "check": "open_alerts",
                "status": "warn",
                "detail": f"{len(open_alerts)} unresolved alert(s)",
            })

        if registry.count_audits() == 0 and transactions:
            findings.append({
                "check": "audit_trail",
                "status": "warn",
                "detail": "no audit records for existing transactions",
            })

        return findings

    def is_compliant(self, registry: FinanceRegistry) -> bool:
        return not any(finding["status"] == "fail"
                       for finding in self.run(registry))

    def status(self, registry: FinanceRegistry) -> str:
        findings = self.run(registry)
        if any(finding["status"] == "fail" for finding in findings):
            return "non_compliant"
        if findings:
            return "attention"
        return "compliant"
