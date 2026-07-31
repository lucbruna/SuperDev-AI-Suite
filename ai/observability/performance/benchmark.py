"""Performance benchmarks."""

from __future__ import annotations

import contextlib
import time
from collections.abc import Callable
from typing import Any


class Benchmark:
    def __init__(self, name: str) -> None:
        self.name = name
        self._results: list[dict[str, Any]] = []

    def run(self, func: Callable[[], Any], iterations: int = 10) -> dict[str, Any]:
        durations = []
        for _ in range(iterations):
            start = time.time()
            with contextlib.suppress(Exception):
                func()
            durations.append((time.time() - start) * 1000)
        result = {
            "name": self.name,
            "iterations": iterations,
            "min_ms": min(durations),
            "max_ms": max(durations),
            "avg_ms": sum(durations) / len(durations),
            "success_rate": sum(1 for d in durations if d > 0) / iterations,
        }
        self._results.append(result)
        return result

    def get_results(self) -> list[dict[str, Any]]:
        return list(self._results)

    def get_latest(self) -> dict[str, Any]:
        return self._results[-1] if self._results else {}


class BenchmarkSuite:
    def __init__(self) -> None:
        self._benchmarks: dict[str, Benchmark] = {}

    def add_benchmark(self, name: str) -> Benchmark:
        b = Benchmark(name)
        self._benchmarks[name] = b
        return b

    def run_all(self) -> dict[str, Any]:
        results = {}
        for name, b in self._benchmarks.items():
            results[name] = b.get_latest()
        return results

    def list_benchmarks(self) -> list[str]:
        return list(self._benchmarks.keys())

    def remove_benchmark(self, name: str) -> bool:
        if name in self._benchmarks:
            del self._benchmarks[name]
            return True
        return False
