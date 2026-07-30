from __future__ import annotations

import time
from typing import Any


class TelemetryCollector:
    """Collects telemetry events from LLM operations."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def record_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        self._events.append({
            "event_type": event_type,
            "data": data or {},
            "timestamp": time.time(),
        })

    def get_events(
        self,
        event_type: str | None = None,
        since: float | None = None,
    ) -> list[dict[str, Any]]:
        filtered = self._events
        if event_type:
            filtered = [e for e in filtered if e["event_type"] == event_type]
        if since is not None:
            filtered = [e for e in filtered if e["timestamp"] >= since]
        return filtered

    def get_summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for event in self._events:
            et = event["event_type"]
            counts[et] = counts.get(et, 0) + 1
        return counts

    @property
    def total_events(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_events": self.total_events,
            "event_types": self.get_summary(),
        }
