"""Forecast engine: projects metric trends forward.

Uses simple linear regression over the snapshot series (with a damped
extrapolation) — deterministic, dependency-free, and honest about the
uncertainty of the projection.
"""
from __future__ import annotations

import math
from typing import Any

from modules.architecture_intelligence.core.history import MetricHistory

_METRICS = ("nodes", "edges", "score")


class ForecastEngine:
    """Projects each numeric metric `horizon` steps ahead."""

    def __init__(self, history: MetricHistory, horizon: int = 5) -> None:
        self.history = history
        self.horizon = max(horizon, 1)

    def run(self) -> dict[str, Any]:
        series = self.history.load()
        if len(series) < 2:
            return {
                "available": True,
                "count": len(series),
                "forecasts": [],
                "message": "Not enough history to forecast (need >= 2 snapshots).",
            }

        forecasts: list[dict[str, Any]] = []
        for metric in _METRICS:
            timestamps, values = self.history.series(metric)
            if len(values) < 2:
                continue
            projection = _linear_forecast(timestamps, values, self.horizon)
            forecasts.append(
                {
                    "metric": metric,
                    "last": values[-1],
                    "projected": [round(v, 2) for v in projection["points"]],
                    "slope_per_step": round(projection["slope"], 3),
                    "direction": "up" if projection["slope"] > 0 else "down",
                }
            )
        return {"available": True, "count": len(series), "forecasts": forecasts}


def _linear_forecast(
    timestamps: list[float], values: list[float], steps: int
) -> dict[str, Any]:
    n = len(values)
    if n == 0:
        return {"slope": 0.0, "points": []}
    x_mean = sum(timestamps) / n
    y_mean = sum(values) / n
    num = sum((t - x_mean) * (v - y_mean) for t, v in zip(timestamps, values))
    den = sum((t - x_mean) ** 2 for t in timestamps)
    slope = num / den if den else 0.0
    intercept = y_mean - slope * x_mean

    # Damp the slope so far extrapolations do not run away.
    last_t = timestamps[-1]
    points: list[float] = []
    for step in range(1, steps + 1):
        t = last_t + step * (timestamps[-1] - timestamps[0]) / max(n - 1, 1)
        raw = intercept + slope * t
        damped = values[-1] + (raw - values[-1]) * (0.5 ** (step - 1))
        points.append(damped if math.isfinite(damped) else values[-1])
    return {"slope": slope, "points": points}
