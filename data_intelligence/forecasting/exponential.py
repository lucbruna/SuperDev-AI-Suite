"""Exponential smoothing forecasting."""

from __future__ import annotations

from data_intelligence.forecasting.base import (ForecastError, Forecaster)


class ExponentialSmoothingForecaster(Forecaster):
    """Weighted average that favours recent observations."""

    def __init__(self, alpha: float = 0.3) -> None:
        self.alpha = alpha

    def fit(self, values: list[float]) -> "ExponentialSmoothingForecaster":
        if not values:
            raise ForecastError("cannot fit an empty series")
        level = float(values[0])
        for value in values[1:]:
            level = self.alpha * float(value) + (1 - self.alpha) * level
        self.level = level
        return self

    def forecast(self, steps: int) -> list[float]:
        return [self.level] * steps
