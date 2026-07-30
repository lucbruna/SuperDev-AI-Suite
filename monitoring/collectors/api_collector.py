from __future__ import annotations

import time
from typing import Any


class ApiCollector:
    """Collects API endpoint metrics."""

    def __init__(self) -> None:
        self._request_count = 0
        self._total_latency = 0.0
        self._error_count = 0
        self._status_counts: dict[int, int] = {}

    def record_request(self, latency: float, status_code: int) -> None:
        self._request_count += 1
        self._total_latency += latency
        if status_code >= 400:
            self._error_count += 1
        self._status_counts[status_code] = (
            self._status_counts.get(status_code, 0) + 1
        )

    def collect(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "request_count": self._request_count,
            "total_latency": round(self._total_latency, 3),
            "error_count": self._error_count,
            "status_counts": dict(self._status_counts),
            "timestamp": time.time(),
        }
        if self._request_count > 0:
            data["avg_latency"] = round(
                self._total_latency / self._request_count, 3
            )
        return data
