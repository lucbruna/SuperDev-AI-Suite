from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class VectorMetrics:
    """Performance metrics for the vector store."""

    def __init__(self):
        self._query_count = 0
        self._index_count = 0
        self._total_query_time = 0.0
        self._total_index_time = 0.0
        self._start_time = datetime.now(timezone.utc)

    def record_query(self, duration_ms: float) -> None:
        self._query_count += 1
        self._total_query_time += duration_ms

    def record_index(self, duration_ms: float) -> None:
        self._index_count += 1
        self._total_index_time += duration_ms

    def snapshot(self) -> dict[str, Any]:
        uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
        return {
            "query_count": self._query_count,
            "index_count": self._index_count,
            "avg_query_ms": self._total_query_time / max(self._query_count, 1),
            "avg_index_ms": self._total_index_time / max(self._index_count, 1),
            "uptime_seconds": uptime,
        }

    def reset(self) -> None:
        self._query_count = 0
        self._index_count = 0
        self._total_query_time = 0.0
        self._total_index_time = 0.0
        self._start_time = datetime.now(timezone.utc)
