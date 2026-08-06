"""Forecasting subsystem configuration."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ForecastConfig:
    """Deterministic forecasting behaviour."""

    growth_method: str = "linear"  # linear | weighted
    debt_interest_rate: float = 0.05
    capacity_growth_rate: float = 0.02
    default_horizon: int = 12
