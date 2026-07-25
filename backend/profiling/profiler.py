from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProfileResult:
    name: str
    duration_ms: float
    details: dict[str, Any] = field(default_factory=dict)


class Profiler:
    """Performance profiler."""

    def __init__(self):
        self._results: list[ProfileResult] = []
        self._active: dict[str, float] = {}

    def start(self, name: str) -> None:
        self._active[name] = time.time()

    def stop(self, name: str) -> ProfileResult | None:
        start_time = self._active.pop(name, None)
        if start_time is None:
            return None
        duration = (time.time() - start_time) * 1000
        result = ProfileResult(name=name, duration_ms=duration)
        self._results.append(result)
        return result

    def get_results(self, name: str | None = None) -> list[ProfileResult]:
        if name:
            return [r for r in self._results if r.name == name]
        return list(self._results)

    def get_summary(self) -> dict[str, Any]:
        if not self._results:
            return {"total": 0}
        by_name: dict[str, list[float]] = {}
        for r in self._results:
            by_name.setdefault(r.name, []).append(r.duration_ms)
        return {
            "total": len(self._results),
            "by_name": {
                name: {
                    "count": len(durations),
                    "avg_ms": sum(durations) / len(durations),
                    "min_ms": min(durations),
                    "max_ms": max(durations),
                }
                for name, durations in by_name.items()
            },
        }

    def clear(self) -> None:
        self._results.clear()
        self._active.clear()


profiler = Profiler()
