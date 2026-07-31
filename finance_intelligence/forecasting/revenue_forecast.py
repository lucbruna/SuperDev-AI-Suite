"""Revenue forecasting for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import (Forecast, Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id, round_money


class RevenueForecast:
    """Project future revenue from historical inflows."""

    def __init__(self) -> None:
        self._records: dict[str, Forecast] = {}

    def forecast(self, transactions: list[Transaction],
                 periods: int = 3) -> Forecast:
        amounts = [tx.amount for tx in transactions
                   if tx.kind in (TransactionType.REVENUE,
                                  TransactionType.RECEIPT)]
        average = self._average(amounts)
        confidence = self._confidence(amounts, average)
        value = round_money(average * periods)
        forecast = Forecast(
            forecast_id=new_id("forecast"),
            kind="revenue",
            horizon=f"{periods}m",
            value=value,
            confidence=confidence,
            details={"periods": periods, "samples": len(amounts),
                     "monthly_average": average})
        self._records[forecast.forecast_id] = forecast
        return forecast

    def _average(self, amounts: list[float]) -> float:
        if not amounts:
            return 0.0
        return round_money(sum(amounts) / len(amounts))

    def _confidence(self, amounts: list[float],
                    average: float) -> float:
        if len(amounts) < 2 or average <= 0.0:
            return 0.5
        variance = sum((amount - average) ** 2
                       for amount in amounts) / len(amounts)
        stddev = variance ** 0.5
        return round(max(0.0, min(1.0, 1.0 - stddev / average)), 2)

    def list(self) -> list[Forecast]:
        return list(self._records.values())
