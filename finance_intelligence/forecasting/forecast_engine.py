"""Forecasting subsystem facade (Volume 35).

Aggregates revenue, expense and cash forecasters.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.forecasting.cash_forecast import CashForecast
from finance_intelligence.forecasting.expense_forecast import (
    ExpenseForecast)
from finance_intelligence.forecasting.revenue_forecast import (
    RevenueForecast)


class ForecastEngine:
    """Aggregate facade over the forecasting subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.revenue = RevenueForecast()
        self.expense = ExpenseForecast()
        self.cash = CashForecast()

    # -- convenience ---------------------------------------------------------
    def forecast(self, kind: str = "all", periods: int = 3,
                 opening_balance: float = 0.0) -> dict[str, Any]:
        transactions = self.registry.list_transactions()
        results: dict[str, Any] = {}
        if kind in ("all", "revenue"):
            results["revenue"] = self.revenue.forecast(
                transactions, periods)
        if kind in ("all", "expense"):
            results["expense"] = self.expense.forecast(
                transactions, periods)
        if kind in ("all", "cash"):
            results["cash"] = self.cash.forecast(
                transactions, periods, opening_balance)
        self.metrics.increment("fi.forecasts")
        self.events.publish(FinanceEventType.FORECAST_GENERATED,
                            {"kind": kind, "periods": periods,
                             "results": list(results)})
        return results

    def stats(self) -> dict[str, Any]:
        forecasts = (self.revenue.list() + self.expense.list()
                     + self.cash.list())
        return {
            "forecasts": len(forecasts),
            "generated": self.metrics.count("fi.forecasts"),
            "by_kind": {kind: sum(1 for forecast in forecasts
                                  if forecast.kind == kind)
                        for kind in ("revenue", "expense", "cash")},
        }
