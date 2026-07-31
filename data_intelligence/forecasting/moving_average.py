"""Moving average forecasting."""

from __future__ import annotations

from data_intelligence.forecasting.base import (ForecastError, Forecaster)


class MovingAverageForecaster(Forecaster):
    """Averages the last window values; extends recursively for longer
    horizons."""

    def __init__(self, window: int = 3) -> None:
        self.window = window

    def fit(self, values: list[float]) -> "MovingAverageForecaster":
        if not values:
            raise ForecastError("cannot fit an empty series")
        if len(values) < self.window:
            raise ForecastError(
                f"series too short for window {self.window}")
        self.values = [float(value) for value in values]
        return self

    def forecast(self, steps: int) -> list[float]:
        series = list(self.values)
        out = []
        for _ in range(steps):
            nxt = sum(series[-self.window:]) / self.window
            out.append(nxt)
            series.append(nxt)
        return out
