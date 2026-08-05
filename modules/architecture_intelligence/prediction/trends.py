"""Trend analysis over the metric history series."""
from __future__ import annotations

from typing import Any

from modules.architecture_intelligence.core.history import MetricHistory


class TrendAnalyzer:
    """Computes per-metric direction and magnitude from snapshots."""

    _METRICS = (
        ("nodes", "nodes", "increasing", "decreasing"),
        ("edges", "edges", "increasing", "decreasing"),
        ("score", "score", "improving", "declining"),
    )

    def __init__(self, history: MetricHistory) -> None:
        self.history = history

    def analyze(self, *, window: int = 10) -> dict[str, Any]:
        snapshots = self.history.recent(window)
        if len(snapshots) < 2:
            return {
                "available": True,
                "count": len(snapshots),
                "trends": [],
                "message": "Not enough history yet (need >= 2 snapshots).",
            }

        trends: list[dict[str, Any]] = []
        for key, label, up_label, down_label in self._METRICS:
            values = [float(s.get(key, 0.0)) for s in snapshots]
            first, last = values[0], values[-1]
            if first == last:
                direction = "stable"
            else:
                direction = up_label if last > first else down_label
            delta = last - first
            pct = (delta / first * 100.0) if first else 0.0
            trends.append(
                {
                    "metric": key,
                    "label": label,
                    "first": first,
                    "last": last,
                    "delta": delta,
                    "percent": round(pct, 2),
                    "direction": direction,
                }
            )
        return {"available": True, "count": len(snapshots), "trends": trends}
