"""Cash projection for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import Forecast, Transaction
from finance_intelligence.finance_protocols import new_id, round_money
from finance_intelligence.finance_registry import FinanceRegistry


class CashProjection:
    """Project day-by-day cash balance over a horizon."""

    def __init__(self, registry: FinanceRegistry,
                 events: FinanceEvents,
                 metrics: FinanceMetrics) -> None:
        self.registry = registry
        self.events = events
        self.metrics = metrics

    def project(self, opening_balance: float, horizon_days: int = 30,
                inflows: list[Transaction] | None = None,
                outflows: list[Transaction] | None = None) -> Forecast:
        inflows = inflows or self._registered(0)  # 0 = inflow marker
        outflows = outflows or self._registered(1)
        balance = round_money(opening_balance)
        days: list[dict[str, float]] = []
        min_balance = balance
        max_balance = balance
        for day in range(1, horizon_days + 1):
            day_in = sum(tx.amount for tx in inflows
                         if tx.created_at and tx.created_at == day)
            day_out = sum(tx.amount for tx in outflows
                          if tx.created_at and tx.created_at == day)
            balance = round_money(balance + day_in - day_out)
            min_balance = min(min_balance, balance)
            max_balance = max(max_balance, balance)
            days.append({"day": day, "balance": balance})
        forecast = Forecast(
            forecast_id=new_id("forecast"), kind="cashflow",
            horizon=f"{horizon_days}d", value=balance, confidence=0.7,
            details={"opening_balance": round_money(opening_balance),
                     "closing_balance": balance,
                     "min_balance": min_balance,
                     "max_balance": max_balance,
                     "days": days})
        self.metrics.increment("fi.forecasts")
        self.events.publish(FinanceEventType.FORECAST_GENERATED,
                            {"forecast_id": forecast.forecast_id,
                             "horizon": forecast.horizon,
                             "value": forecast.value})
        return forecast

    def series(self, forecast: Forecast) -> list[dict[str, float]]:
        return list(forecast.details.get("days", []))

    def _registered(self, kind: int) -> list[Transaction]:
        from finance_intelligence.finance_models import TransactionType
        target = (TransactionType.REVENUE if kind == 0
                  else TransactionType.EXPENSE)
        return [tx for tx in self.registry.list_transactions()
                if tx.kind == target]
