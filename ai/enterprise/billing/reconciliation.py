"""Billing reconciliation."""
from __future__ import annotations

import time
from typing import Any


class ReconciliationManager:
    def __init__(self) -> None:
        self._reconciliations: list[dict[str, Any]] = []
    def reconcile(self, org_id: str, period_start: float, period_end: float, charges: list[dict[str, Any]], payments: list[dict[str, Any]]) -> dict[str, Any]:
        total_charges = sum(c.get("amount", 0) for c in charges)
        total_payments = sum(p.get("amount", 0) for p in payments)
        difference = total_charges - total_payments
        result = {"org_id": org_id, "period_start": period_start, "period_end": period_end, "total_charges": total_charges, "total_payments": total_payments, "difference": difference, "status": "balanced" if difference == 0 else "unbalanced", "reconciled_at": time.time()}
        self._reconciliations.append(result)
        return result
    def get_history(self, org_id: str = "", limit: int = 50) -> list[dict[str, Any]]:
        results = self._reconciliations
        if org_id:
            results = [r for r in results if r["org_id"] == org_id]
        return results[-limit:]
    def get_discrepancies(self) -> list[dict[str, Any]]:
        return [r for r in self._reconciliations if r["status"] == "unbalanced"]
    def count(self) -> int:
        return len(self._reconciliations)
