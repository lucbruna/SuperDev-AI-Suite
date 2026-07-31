"""Reconciliation for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_registry import FinanceRegistry


class Reconciliation:
    """Compare expected balances against the recorded ledger."""

    def __init__(self, registry: FinanceRegistry,
                 events: FinanceEvents) -> None:
        self.registry = registry
        self.events = events

    def reconcile(self, account_id: str,
                  expected_balance: float) -> dict[str, Any]:
        account = self.registry.get_account(account_id)
        if account is None:
            return {"account_id": account_id, "status": "not_found"}
        actual = round(account.balance, 2)
        expected = round(float(expected_balance), 2)
        difference = round(expected - actual, 2)
        matched = abs(difference) < 1e-9
        result = {
            "account_id": account_id,
            "expected": expected,
            "actual": actual,
            "difference": difference,
            "status": "matched" if matched else "difference",
        }
        if not matched:
            self.events.publish(FinanceEventType.ANOMALY_DETECTED,
                                {"account_id": account_id,
                                 "difference": difference,
                                 "source": "reconciliation"})
        return result

    def scan_all(self, expected: dict[str, float]) -> list[dict[str, Any]]:
        results = [self.reconcile(account_id, expected_amount)
                   for account_id, expected_amount in expected.items()]
        return [result for result in results
                if result["status"] == "difference"]
