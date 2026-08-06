"""Unit tests: forecasting package."""
from __future__ import annotations

from modules.ai_evolution_engine.forecasting.forecast_engine import (
    Forecast,
    ForecastEngine,
    compounding_projection,
    linear_projection,
)
from modules.ai_evolution_engine.tests.helpers import make_context


def test_linear_projection():
    assert linear_projection(10.0, 1.0, 3) == [11.0, 12.0, 13.0]


def test_compounding_projection():
    values = compounding_projection(100.0, 0.1, 2)
    assert values == [110.0, 121.0]


def test_forecast_engine_projects_three_series():
    ctx = make_context(
        debt_effort_points=100.0,
        cache_hit_ratio=0.9,
        module_count=5,
    )
    forecasts = ForecastEngine().project(ctx, horizon=4)

    by_name = {f.name: f for f in forecasts}
    assert set(by_name) == {"technical_debt", "capacity", "cache_hit_ratio"}
    assert len(by_name["technical_debt"].values) == 4
    assert len(by_name["capacity"].values) == 4
    # deterministic: repeating yields identical output
    again = ForecastEngine().project(ctx, horizon=4)
    assert [f.to_dict() for f in forecasts] == [f.to_dict() for f in again]


def test_forecast_dataclass_to_dict():
    forecast = Forecast(name="x", values=[1.0], unit="unit")
    assert forecast.to_dict() == {"name": "x", "values": [1.0], "unit": "unit"}
