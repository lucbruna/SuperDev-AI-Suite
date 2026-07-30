from __future__ import annotations

import time
from typing import Any


class PlannerProfiler:
    """Profiling for plan execution performance."""

    def __init__(self):
        self._metrics: dict[str, list[float]] = {}

    def start(self, label: str) -> None:
        if label not in self._metrics:
            self._metrics[label] = []
        self._metrics[label].append(time.time())

    def end(self, label: str) -> float | None:
        if label not in self._metrics or not self._metrics[label]:
            return None
        start_time = self._metrics[label][-1]
        duration = time.time() - start_time
        self._metrics[label][-1] = duration
        return duration

    def summary(self) -> dict[str, Any]:
        result = {}
        for label, values in self._metrics.items():
            if values:
                result[label] = {
                    "count": len(values),
                    "total": round(sum(values), 4),
                    "avg": round(sum(values) / len(values), 4),
                }
        return result

    def reset(self) -> None:
        self._metrics.clear()
