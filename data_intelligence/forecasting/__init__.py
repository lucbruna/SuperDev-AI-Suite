"""Forecasting subsystem (Volume 22).

Historical series (e.g. 3 years of supermarket sales with weather, dates,
region and promotions) projected with naive, seasonal, moving average,
exponential smoothing and seasonal-factor methods.
"""

from __future__ import annotations

from data_intelligence.forecasting.base import (ForecastError, Forecaster)
from data_intelligence.forecasting.engine import (ForecastingEngine, METHODS)
from data_intelligence.forecasting.exponential import (
    ExponentialSmoothingForecaster)
from data_intelligence.forecasting.moving_average import (
    MovingAverageForecaster)
from data_intelligence.forecasting.naive import (NaiveForecaster,
                                                 SeasonalNaiveForecaster)
from data_intelligence.forecasting.seasonal import SeasonalForecaster

__all__ = [
    "ForecastingEngine", "Forecaster", "ForecastError",
    "NaiveForecaster", "SeasonalNaiveForecaster",
    "MovingAverageForecaster", "ExponentialSmoothingForecaster",
    "SeasonalForecaster", "METHODS",
]
