"""Payment prediction for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import time
from typing import Any

from finance_intelligence.finance_models import Invoice


class PaymentPrediction:
    """Predict the likelihood of invoice payment."""

    def predict(self, invoice: Invoice) -> dict[str, Any]:
        score = 0.9
        reasons: list[str] = []
        days_overdue = 0
        if invoice.due_date:
            days_overdue = max(0, (time.time() - invoice.due_date) / 86400)
            if days_overdue > 0:
                penalty = min(0.5, days_overdue * 0.01)
                score -= penalty
                reasons.append(f"{int(days_overdue)} days overdue")
        if invoice.amount > 10000:
            score -= 0.1
            reasons.append("high amount")
        if invoice.paid_amount > 0:
            score += 0.05
            reasons.append("partial payment history")
        score = max(0.0, min(1.0, round(score, 2)))
        expected_days = int(max(0, round(days_overdue + 15)))
        return {
            "invoice_id": invoice.invoice_id,
            "score": score,
            "expected_days": expected_days,
            "reasons": reasons,
        }

    def predict_many(self, invoices: list[Invoice]) -> list[dict[str, Any]]:
        return [self.predict(invoice) for invoice in invoices]

    def at_risk(self, invoices: list[Invoice],
                threshold: float = 0.5) -> list[dict[str, Any]]:
        return [prediction for prediction in self.predict_many(invoices)
                if prediction["score"] < threshold]
