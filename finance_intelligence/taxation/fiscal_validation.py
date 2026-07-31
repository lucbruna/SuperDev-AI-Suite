"""Fiscal validation for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import Transaction
from finance_intelligence.taxation.tax_rules import TaxRules


class FiscalValidation:
    """Validate tax posture: receipts issued, declarations filed."""

    def __init__(self, rules: TaxRules | None = None) -> None:
        self.rules = rules or TaxRules()

    def validate(self, transactions: list[Transaction],
                 declared_amount: float,
                 period: str = "") -> dict[str, Any]:
        total = round(sum(tx.amount for tx in transactions), 2)
        difference = round(declared_amount - total, 2)
        compliant = abs(difference) < 1e-9
        return {
            "period": period,
            "recorded_total": total,
            "declared_amount": declared_amount,
            "difference": difference,
            "compliant": compliant,
            "regime": self.rules.regime.value,
        }

    def checks(self, transactions: list[Transaction]) -> dict[str, bool]:
        has_transactions = len(transactions) > 0
        has_revenue = any(tx.amount > 0 for tx in transactions)
        return {
            "has_transactions": has_transactions,
            "has_revenue": has_revenue,
            "regime_configured": self.rules.applicable_taxes() != [],
        }
