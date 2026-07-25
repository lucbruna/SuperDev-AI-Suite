from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkResult:
    name: str
    iterations: int
    total_ms: float
    avg_ms: float
    min_ms: float
    max_ms: float
    ops_per_second: float


class BenchmarkRunner:
    """Performance benchmark runner."""

    def __init__(self):
        self._results: list[BenchmarkResult] = []

    async def run(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        iterations: int = 100,
        args: tuple = (),
        kwargs: dict[str, Any] | None = None,
    ) -> BenchmarkResult:
        durations: list[float] = []

        for _ in range(iterations):
            start = time.perf_counter()
            await func(*args, **(kwargs or {}))
            elapsed = (time.perf_counter() - start) * 1000
            durations.append(elapsed)

        total = sum(durations)
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_ms=total,
            avg_ms=total / iterations,
            min_ms=min(durations),
            max_ms=max(durations),
            ops_per_second=1000 / (total / iterations) if total > 0 else 0,
        )
        self._results.append(result)
        return result

    def get_results(self) -> list[BenchmarkResult]:
        return list(self._results)

    def clear(self) -> None:
        self._results.clear()


benchmark_runner = BenchmarkRunner()
