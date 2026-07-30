from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class CodeProfiler:
    """Profiles code execution time for functions and code blocks."""

    def __init__(self) -> None:
        self._results: dict[str, list[float]] = {}
        self._enabled = True

    def profile(self, name: str = "") -> Callable[[F], F]:
        def decorator(func: F) -> F:
            label = name or func.__name__

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if not self._enabled:
                    return func(*args, **kwargs)
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = (time.perf_counter() - start) * 1000
                    self._record(label, elapsed)

            return wrapper  # type: ignore[return-value]
        return decorator

    def profile_async(self, name: str = "") -> Callable[[F], F]:
        def decorator(func: F) -> F:
            label = name or func.__name__

            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                if not self._enabled:
                    return await func(*args, **kwargs)
                start = time.perf_counter()
                try:
                    return await func(*args, **kwargs)
                finally:
                    elapsed = (time.perf_counter() - start) * 1000
                    self._record(label, elapsed)

            return wrapper  # type: ignore[return-value]
        return decorator

    def _record(self, name: str, duration_ms: float) -> None:
        if name not in self._results:
            self._results[name] = []
        self._results[name].append(duration_ms)

    def stats(self, name: str = "") -> dict[str, Any]:
        if name:
            durations = self._results.get(name, [])
            return self._compute_stats(name, durations)

        all_stats: dict[str, Any] = {}
        for key, durations in self._results.items():
            all_stats[key] = self._compute_stats(key, durations)
        return all_stats

    def _compute_stats(self, name: str, durations: list[float]) -> dict[str, Any]:
        if not durations:
            return {"name": name, "count": 0}
        sorted_d = sorted(durations)
        n = len(sorted_d)
        return {
            "name": name,
            "count": n,
            "total_ms": round(sum(sorted_d), 2),
            "avg_ms": round(sum(sorted_d) / n, 2),
            "min_ms": round(sorted_d[0], 2),
            "max_ms": round(sorted_d[-1], 2),
            "p50_ms": round(sorted_d[n // 2], 2),
            "p95_ms": round(sorted_d[int(n * 0.95)], 2),
            "p99_ms": round(sorted_d[int(n * 0.99)], 2),
        }

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def clear(self) -> None:
        self._results.clear()
