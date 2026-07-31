"""Naive and seasonal-naive forecasting."""

from __future__ import annotations

from data_intelligence.forecasting.base import (ForecastError, Forecaster)


class NaiveForecaster(Forecaster):
    """Repeats the last observed value for every future step."""

    def fit(self, values: list[float]) -> "NaiveForecaster":
        if not values:
            raise ForecastError("cannot fit an empty series")
        self.last = float(values[-1])
        return self

    def forecast(self, steps: int) -> list[float]:
        return [self.last] * steps


class SeasonalNaiveForecaster(Forecaster):
    """Repeats the value observed at the same season in the last cycle."""

    def __init__(self, season: int = 12) -> None:
        self.season = season

    def fit(self, values: list[float]) -> "SeasonalNaiveForecaster":
        if not values:
            raise ForecastError("cannot fit an empty series")
        if len(values) < self.season:
            raise ForecastError(
                f"series too short for season {self.season}")
        self.values = [float(value) for value in values]
        return self

    def forecast(self, steps: int) -> list[float]:
        out = []
        for step in range(steps):
            index = (-self.season + step) % len(self.values)
            out.append(self.values[index])
        return out
