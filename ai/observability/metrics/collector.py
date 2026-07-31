"""Metrics collector."""

from __future__ import annotations

import time
from typing import Any


class MetricsCollector:
    def __init__(self, buffer_size: int = 1000) -> None:
        self._buffer: list[dict[str, Any]] = []
        self._buffer_size = buffer_size
        self._total_collected = 0

    def collect(
        self, name: str, value: float, labels: dict[str, str] | None = None, metric_type: str = "gauge"
    ) -> bool:
        point = {"name": name, "value": value, "timestamp": time.time(), "labels": labels or {}, "type": metric_type}
        self._buffer.append(point)
        self._total_collected += 1
        if len(self._buffer) >= self._buffer_size:
            self.flush()
        return True

    def increment(self, name: str, amount: float = 1.0, labels: dict[str, str] | None = None) -> None:
        self.collect(name, amount, labels, "counter")

    def flush(self) -> int:
        n = len(self._buffer)
        self._buffer = []
        return n

    def get_buffer(self) -> list[dict[str, Any]]:
        return list(self._buffer)

    def total_collected(self) -> int:
        return self._total_collected
