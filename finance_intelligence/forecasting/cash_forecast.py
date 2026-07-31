"""Cash forecasting for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import (Forecast, Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id, round_money


class CashForecast:
    """Project net cash position from revenue and expense averages."""

    def __init__(self) -> None:
        self._records: dict[str, Forecast] = {}

    def forecast(self, transactions: list[Transaction],
                 periods: int = 3,
                 opening_balance: float = 0.0) -> Forecast:
        inflows = [tx.amount for tx in transactions
                   if tx.kind in (TransactionType.REVENUE,
                                  TransactionType.RECEIPT)]
        outflows = [tx.amount for tx in transactions
                    if tx.kind in (TransactionType.EXPENSE,
                                   TransactionType.PAYMENT)]
        inflow_avg = self._average(inflows)
        outflow_avg = self._average(outflows)
        net_avg = round_money(inflow_avg - outflow_avg)
        value = round_money(opening_balance + net_avg * periods)
        confidence = self._confidence(inflows, outflows)
        forecast = Forecast(
            forecast_id=new_id("forecast"),
            kind="cash",
            horizon=f"{periods}m",
            value=value,
            confidence=confidence,
            details={"periods": periods, "opening_balance": opening_balance,
                     "net_monthly": net_avg})
        self._records[forecast.forecast_id] = forecast
        return forecast

    def _average(self, amounts: list[float]) -> float:
        if not amounts:
            return 0.0
        return round_money(sum(amounts) / len(amounts))

    def _confidence(self, inflows: list[float],
                    outflows: list[float]) -> float:
        samples = len(inflows) + len(outflows)
        if samples < 2:
            return 0.5
        spread = max(len(inflows), len(outflows), 1)
        return round(max(0.0, min(1.0, 1.0 - spread / 10.0)), 2)

    def list(self) -> list[Forecast]:
        return list(self._records.values())
