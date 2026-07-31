"""AI Model metrics."""

from __future__ import annotations


class ModelMetrics:
    def __init__(self) -> None:
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._timers: dict[str, list[float]] = {}
        self._costs: dict[str, float] = {}

    def increment(self, name: str, amount: float = 1.0) -> None:
        self._counters[name] = self._counters.get(name, 0) + amount

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def record_timer(self, name: str, duration_ms: float) -> None:
        self._timers.setdefault(name, []).append(duration_ms)
        if len(self._timers[name]) > 1000:
            self._timers[name] = self._timers[name][-1000:]

    def record_cost(self, model_id: str, amount: float) -> None:
        self._costs[model_id] = self._costs.get(model_id, 0) + amount

    def get_counter(self, name: str) -> float:
        return self._counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float:
        return self._gauges.get(name, 0.0)

    def get_timer_stats(self, name: str) -> dict[str, float]:
        values = self._timers.get(name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}
        return {"min": min(values), "max": max(values), "avg": sum(values) / len(values), "count": len(values)}

    def get_model_cost(self, model_id: str) -> float:
        return self._costs.get(model_id, 0.0)

    def get_total_cost(self) -> float:
        return sum(self._costs.values())

    def clear(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._timers.clear()
        self._costs.clear()
