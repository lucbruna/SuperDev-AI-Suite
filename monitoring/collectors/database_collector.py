from __future__ import annotations

import time
from typing import Any


class DatabaseCollector:
    """Collects database-level performance metrics."""

    def __init__(self) -> None:
        self._query_count = 0
        self._total_latency = 0.0
        self._error_count = 0

    def record_query(self, latency: float) -> None:
        self._query_count += 1
        self._total_latency += latency

    def record_error(self) -> None:
        self._error_count += 1

    def collect(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "query_count": self._query_count,
            "total_latency": round(self._total_latency, 3),
            "error_count": self._error_count,
            "timestamp": time.time(),
        }
        if self._query_count > 0:
            data["avg_latency"] = round(
                self._total_latency / self._query_count, 3
            )
        return data
