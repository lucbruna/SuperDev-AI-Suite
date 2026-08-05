"""Realtime Charts — simulated live data streams for dashboards."""
from __future__ import annotations

import math
import time
from typing import Any


class RealtimeCharts:
    """Generates deterministic live-series samples."""

    def sample(self, *, metric: str = "requests", rate: float = 100.0,
               seed: float | None = None) -> dict[str, Any]:
        seed = seed if seed is not None else time.time()
        wave = rate + rate * 0.15 * math.sin(seed % 6.28)
        jitter = rate * 0.05 * math.sin(seed * 1.7)
        return {
            "metric": metric,
            "value": round(wave + jitter, 2),
            "ts": round(time.time(), 3),
        }


_realtime_charts: RealtimeCharts | None = None


def get_realtime_charts() -> RealtimeCharts:
    global _realtime_charts
    if _realtime_charts is None:
        _realtime_charts = RealtimeCharts()
    return _realtime_charts
