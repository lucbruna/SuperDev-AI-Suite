from __future__ import annotations

from typing import Any, Dict, List


class AgentMetrics:
    """Metrics collection for agents."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}

    def increment(self, key: str, value: int = 1) -> None:
        self._counters[key] = self._counters.get(key, 0) + value

    def gauge(self, key: str, value: float) -> None:
        self._gauges[key] = value

    def get_counter(self, key: str) -> int:
        return self._counters.get(key, 0)

    def get_gauge(self, key: str) -> float:
        return self._gauges.get(key, 0.0)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
        }

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
