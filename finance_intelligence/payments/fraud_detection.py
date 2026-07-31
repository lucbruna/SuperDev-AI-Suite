"""Fraud detection for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import Payment, RiskLevel


class FraudDetection:
    """Heuristic fraud scoring for payments."""

    def __init__(self, events: FinanceEvents, metrics: FinanceMetrics,
                 threshold: float = 0.5) -> None:
        self.events = events
        self.metrics = metrics
        self.threshold = float(threshold)

    def analyze(self, payment: Payment) -> dict[str, Any]:
        reasons: list[str] = []
        score = 0.0
        if payment.amount > 10000:
            score += 0.5
            reasons.append("amount above threshold")
        if payment.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            score += 0.5
            reasons.append("high risk level")
        if not payment.counterparty.strip():
            score += 0.2
            reasons.append("missing counterparty")
        score = min(1.0, round(score, 2))
        flagged = score >= self.threshold
        result = {"payment_id": payment.payment_id, "score": score,
                  "flagged": flagged, "reasons": reasons}
        if flagged:
            self.metrics.increment("fi.fraud.flagged")
            self.events.publish(FinanceEventType.FRAUD_DETECTED,
                                {"payment_id": payment.payment_id,
                                 "score": score})
        return result

    def set_threshold(self, value: float) -> None:
        self.threshold = float(value)
