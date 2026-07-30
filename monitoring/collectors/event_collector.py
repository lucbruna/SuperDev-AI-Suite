from __future__ import annotations

import time
from typing import Any


class EventCollector:
    """Collects application event metrics."""

    def __init__(self) -> None:
        self._event_counts: dict[str, int] = {}
        self._total_events = 0

    def record_event(self, event_type: str) -> None:
        self._event_counts[event_type] = (
            self._event_counts.get(event_type, 0) + 1
        )
        self._total_events += 1

    def collect(self) -> dict[str, Any]:
        return {
            "total_events": self._total_events,
            "event_counts": dict(self._event_counts),
            "unique_types": len(self._event_counts),
            "timestamp": time.time(),
        }
