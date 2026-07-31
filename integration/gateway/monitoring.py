from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any


class GatewayMonitoring:
    """Records request volume, latency, and error rates through the gateway."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.gateway.monitoring")
        self._requests: dict[str, int] = defaultdict(int)
        self._latencies: dict[str, list[float]] = defaultdict(list)
        self._errors: dict[str, int] = defaultdict(int)
        self._started = time.monotonic()

    def record_request(self, route: str, latency: float, status: str = "ok") -> None:
        self._requests[route] += 1
        self._latencies[route].append(latency)
        if status != "ok":
            self._errors[route] += 1

    def total_requests(self) -> int:
        return sum(self._requests.values())

    def total_errors(self) -> int:
        return sum(self._errors.values())

    def error_rate(self) -> float:
        total = self.total_requests()
        return round(self.total_errors() / total, 4) if total else 0.0

    def average_latency(self, route: str | None = None) -> float:
        if route is None:
            samples = [lat for lats in self._latencies.values() for lat in lats]
        else:
            samples = self._latencies.get(route, [])
        return round(sum(samples) / len(samples), 4) if samples else 0.0

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_requests": self.total_requests(),
            "total_errors": self.total_errors(),
            "error_rate": self.error_rate(),
            "average_latency": self.average_latency(),
            "routes": dict(self._requests),
            "uptime_seconds": round(time.monotonic() - self._started, 3),
        }
