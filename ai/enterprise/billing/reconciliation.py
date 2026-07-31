"""Billing reconciliation."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ReconciliationManager:
    def __init__(self) -> None:
        self._reconciliations: List[Dict[str, Any]] = []
    def reconcile(self, org_id: str, period_start: float, period_end: float, charges: List[Dict[str, Any]], payments: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_charges = sum(c.get("amount", 0) for c in charges)
        total_payments = sum(p.get("amount", 0) for p in payments)
        difference = total_charges - total_payments
        result = {"org_id": org_id, "period_start": period_start, "period_end": period_end, "total_charges": total_charges, "total_payments": total_payments, "difference": difference, "status": "balanced" if difference == 0 else "unbalanced", "reconciled_at": time.time()}
        self._reconciliations.append(result)
        return result
    def get_history(self, org_id: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        results = self._reconciliations
        if org_id:
            results = [r for r in results if r["org_id"] == org_id]
        return results[-limit:]
    def get_discrepancies(self) -> List[Dict[str, Any]]:
        return [r for r in self._reconciliations if r["status"] == "unbalanced"]
    def count(self) -> int:
        return len(self._reconciliations)
