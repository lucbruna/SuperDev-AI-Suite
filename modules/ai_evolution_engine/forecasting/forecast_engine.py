"""Forecast engine: deterministic projections of platform metrics."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.forecast_config import ForecastConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class Forecast:
    """A deterministic projection series."""

    name: str
    values: list[float] = field(default_factory=list)
    unit: str = ""

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "values": list(self.values), "unit": self.unit}


def linear_projection(current: float, delta_per_period: float, horizon: int) -> list[float]:
    return [round(current + delta_per_period * i, 2) for i in range(1, horizon + 1)]


def compounding_projection(current: float, growth_rate: float, horizon: int) -> list[float]:
    values: list[float] = []
    value = current
    for _ in range(horizon):
        value = value * (1.0 + growth_rate)
        values.append(round(value, 2))
    return values


class ForecastEngine:
    """Computes forecasts from current values and configured growth rates."""

    def __init__(self, config: ForecastConfig | None = None) -> None:
        self._config = config or ForecastConfig()

    def project(
        self, ctx: EvolutionContext, horizon: int | None = None
    ) -> list[Forecast]:
        h = horizon or self._config.default_horizon
        debt_points = float(ctx.get_artifact("debt_effort_points", 0.0) or 0.0)
        cache_hit = float(ctx.get_artifact("cache_hit_ratio", 1.0) or 1.0)
        modules = int(ctx.get_artifact("module_count", 1) or 1)

        debt = Forecast(
            name="technical_debt",
            values=compounding_projection(debt_points, self._config.debt_interest_rate, h),
            unit="points",
        )
        capacity = Forecast(
            name="capacity",
            values=compounding_projection(float(modules), self._config.capacity_growth_rate, h),
            unit="modules",
        )
        cache = Forecast(
            name="cache_hit_ratio",
            values=linear_projection(cache_hit, 0.01, h),
            unit="ratio",
        )
        return [debt, capacity, cache]
