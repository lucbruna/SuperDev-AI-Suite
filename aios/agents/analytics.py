"""AnalyticsAgent: deterministic statistics and trend detection."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent


class AnalyticsAgent(BaseAgent):
    def __init__(self, name: str = "analytics", **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="analytics",
            capabilities=["data_analysis", "reporting", "trend_detection"],
            description="Computes statistics and detects trends",
            **kwargs,
        )

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        data = input_data if isinstance(input_data, (list, tuple)) else list(input_data.get("data", []))
        values = [float(v) for v in data if isinstance(v, (int, float))]
        if not values:
            return {"count": 0, "status": "empty"}
        total = sum(values)
        mean = total / len(values)
        trend = "up" if values[-1] > values[0] else ("down" if values[-1] < values[0] else "flat")
        pct_change = round((values[-1] - values[0]) / values[0] * 100, 2) if values[0] != 0 else 0.0
        return {
            "count": len(values),
            "sum": round(total, 4),
            "mean": round(mean, 4),
            "min": min(values),
            "max": max(values),
            "trend": trend,
            "pct_change": pct_change,
            "status": "ok",
        }
