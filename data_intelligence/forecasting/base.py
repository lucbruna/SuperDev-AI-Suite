"""Base classes for forecasting."""

from __future__ import annotations

from typing import Any


class ForecastError(Exception):
    """Raised when a forecast cannot be computed."""


class Forecaster:
    """Fits a historical series and produces point forecasts."""

    def fit(self, values: Any) -> "Forecaster":
        raise NotImplementedError

    def forecast(self, steps: int) -> list[float]:
        raise NotImplementedError
