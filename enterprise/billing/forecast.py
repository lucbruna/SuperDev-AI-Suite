from __future__ import annotations

from decimal import Decimal

from .cost_analyzer import CostForecast

__all__ = ["CostForecast"]


def forecast_report(forecaster: CostForecast) -> str:
    data = forecaster.forecast(30)
    return (
        f"Daily average: ${data['avg_daily']}\n"
        f"Projected 30d: ${data['projected']}\n"
        f"Based on {data['days_analyzed']} days"
    )