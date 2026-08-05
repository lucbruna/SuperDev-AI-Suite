"""Predictive Analysis — simple linear-trend forecasting."""
from __future__ import annotations

from typing import Any


class PredictiveAnalysis:
    """Forecasts the next value of a series by linear regression."""

    def forecast(self, series: list[float], *, horizon: int = 1) -> dict[str, Any]:
        n = len(series)
        if n < 2:
            return {"ok": False, "error": "need at least 2 points", "forecast": None}
        xs = list(range(n))
        mean_x = sum(xs) / n
        mean_y = sum(series) / n
        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, series, strict=False)) / \
            (sum((x - mean_x) ** 2 for x in xs) or 1.0)
        intercept = mean_y - slope * mean_x
        forecast = [round(slope * (n + i) + intercept, 2) for i in range(horizon)]
        return {
            "slope": round(slope, 3),
            "intercept": round(intercept, 3),
            "forecast": forecast,
            "horizon": horizon,
        }


_predictive_analysis: PredictiveAnalysis | None = None


def get_predictive_analysis() -> PredictiveAnalysis:
    global _predictive_analysis
    if _predictive_analysis is None:
        _predictive_analysis = PredictiveAnalysis()
    return _predictive_analysis
