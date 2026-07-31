"""Liquidity analysis for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import datetime
from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_models import RiskLevel, Transaction
from finance_intelligence.finance_protocols import round_money
from finance_intelligence.finance_registry import FinanceRegistry


class LiquidityAnalysis:
    """Liquidity metrics and monthly cash summaries."""

    def __init__(self, registry: FinanceRegistry,
                 events: FinanceEvents) -> None:
        self.registry = registry
        self.events = events

    def analyze(self, opening_balance: float,
                inflows: list[Transaction],
                outflows: list[Transaction]) -> dict[str, Any]:
        total_in = round_money(sum(tx.amount for tx in inflows))
        total_out = round_money(sum(tx.amount for tx in outflows))
        net_flow = round_money(total_in - total_out)
        closing = round_money(opening_balance + net_flow)
        daily_out = round_money(total_out / 30) if total_out > 0 else 0.0
        coverage_days = round_money(closing / daily_out) if daily_out > 0 \
            else 0.0
        ratio = round_money(total_in / total_out) if total_out > 0 else 1.0
        if closing >= 0 and ratio >= 1:
            status = "healthy"
        elif closing >= 0 and ratio < 1:
            status = "warning"
        else:
            status = "critical"
        result = {
            "opening_balance": round_money(opening_balance),
            "total_inflows": total_in,
            "total_outflows": total_out,
            "net_flow": net_flow,
            "closing_balance": closing,
            "coverage_days": coverage_days,
            "liquidity_ratio": ratio,
            "status": status,
        }
        if status == "critical":
            self.events.publish(FinanceEventType.RISK_FLAGGED,
                                {"level": RiskLevel.CRITICAL.value,
                                 "source": "liquidity",
                                 "closing_balance": closing})
        return result

    def monthly_summary(self,
                        transactions: list[Transaction]) -> dict[str, Any]:
        from finance_intelligence.finance_models import TransactionType
        months: dict[str, dict[str, float]] = {}
        for transaction in transactions:
            month = datetime.datetime.fromtimestamp(
                transaction.created_at).strftime("%Y-%m")
            bucket = months.setdefault(
                month, {"inflows": 0.0, "outflows": 0.0})
            if transaction.kind == TransactionType.REVENUE:
                bucket["inflows"] = round_money(
                    bucket["inflows"] + transaction.amount)
            else:
                bucket["outflows"] = round_money(
                    bucket["outflows"] + transaction.amount)
        return {"months": months, "count": len(months)}
