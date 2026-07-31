from __future__ import annotations

import logging
from typing import Any


class AnalyticsTrends:
    """Forecast and seasonality analysis for metric series."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.analytics.trends")

    def render(self) -> dict[str, Any]:
        return {"methods": ["forecast", "seasonality"]}

    def forecast(self, series: list[dict[str, Any]], horizon: int = 30) -> list[dict[str, Any]]:
        last = series[-1]["value"] if series else 0.0
        return [
            {"point": len(series) + i + 1, "value": last}
            for i in range(horizon)
        ]

    def seasonality(self, series: list[dict[str, Any]]) -> dict[str, Any]:
        values = [float(s.get("value", 0)) for s in series]
        return {
            "points": len(values),
            "mean": round(sum(values) / len(values), 2) if values else 0.0,
            "min": min(values) if values else 0.0,
            "max": max(values) if values else 0.0,
        }
