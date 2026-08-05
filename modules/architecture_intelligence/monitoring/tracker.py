"""Monitoring: metric history tracking with snapshot cadence.

The tracker feeds MetricHistory with periodic snapshots; the engine's
forecast/trends read from the same store.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class MetricTracker:
    def __init__(self, history: Any) -> None:
        self.history = history

    def track(self, metrics: dict[str, Any], *, min_interval_seconds: float = 60.0) -> bool:
        return self.history.append(metrics, min_interval_seconds=min_interval_seconds)

    def last_snapshot(self) -> dict[str, Any] | None:
        recent = self.history.recent(limit=1)
        return recent[0] if recent else None

    def status(self) -> dict[str, Any]:
        return {
            "samples": self.history.count(),
            "last": self.last_snapshot(),
            "tracked_at": datetime.now(timezone.utc).isoformat(),
        }


def get_tracker(engine: Any) -> MetricTracker:
    return MetricTracker(engine.history)
