"""Benchmark management for comparing agent performance."""

from __future__ import annotations

from typing import Any


class BenchmarkManager:
    """Manages performance benchmarks and comparison."""

    def __init__(self) -> None:
        self._benchmarks: dict[str, dict[str, Any]] = {}
        self._defaults = {
            "speed": 0.7,
            "accuracy": 0.8,
            "completeness": 0.75,
            "efficiency": 0.7,
        }

    def set_benchmark(self, name: str, values: dict[str, float]) -> None:
        self._benchmarks[name] = dict(values)

    def compare(self, agent_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
        benchmark = self._benchmarks.get("default", self._defaults)
        comparison: dict[str, Any] = {}
        meets_all = True
        for key, target in benchmark.items():
            actual = float(metrics.get(key, 0.0))
            diff = round(actual - target, 3)
            meets = diff >= 0
            comparison[key] = {"target": target, "actual": actual, "diff": diff, "meets": meets}
            if not meets:
                meets_all = False
        return {
            "agent_id": agent_id,
            "meets_benchmark": meets_all,
            "details": comparison,
        }

    def get_benchmarks(self) -> dict[str, dict[str, float]]:
        return dict(self._benchmarks)
