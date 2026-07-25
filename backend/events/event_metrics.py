from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime


class EventMetrics:
    """Event usage metrics."""

    def __init__(self):
        self._counts: dict[str, int] = defaultdict(int)
        self._timestamps: dict[str, list[datetime]] = defaultdict(list)

    def record(self, event_type: str) -> None:
        self._counts[event_type] += 1
        self._timestamps[event_type].append(datetime.now(UTC))

    def get_count(self, event_type: str) -> int:
        return self._counts.get(event_type, 0)

    def get_all_counts(self) -> dict[str, int]:
        return dict(self._counts)

    def get_recent(self, event_type: str, minutes: int = 60) -> int:
        from datetime import timedelta
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)
        return sum(1 for t in self._timestamps.get(event_type, []) if t >= cutoff)
