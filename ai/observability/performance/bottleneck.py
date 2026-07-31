"""Bottleneck detection."""
from __future__ import annotations

from typing import Any


class BottleneckDetector:
    def __init__(self, threshold_percent: float = 80.0) -> None:
        self._threshold = threshold_percent
        self._measurements: dict[str, list[float]] = {}
    def record(self, component: str, duration_ms: float) -> None:
        self._measurements.setdefault(component, []).append(duration_ms)
        if len(self._measurements[component]) > 1000:
            self._measurements[component] = self._measurements[component][-1000:]
    def detect(self) -> list[dict[str, Any]]:
        bottlenecks = []
        all_avgs = {}
        for comp, values in self._measurements.items():
            all_avgs[comp] = sum(values) / len(values) if values else 0
        total = sum(all_avgs.values()) or 1
        for comp, avg in all_avgs.items():
            percent = (avg / total) * 100
            if percent > self._threshold:
                bottlenecks.append({"component": comp, "avg_ms": avg, "percent_of_total": percent})
        return sorted(bottlenecks, key=lambda x: x["percent_of_total"], reverse=True)
    def list_components(self) -> list[str]:
        return list(self._measurements.keys())
    def clear(self) -> int:
        n = sum(len(v) for v in self._measurements.values())
        self._measurements.clear()
        return n
