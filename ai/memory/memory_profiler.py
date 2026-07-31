from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class ProfileSample:
    """A single profiling sample."""

    def __init__(self, operation: str, duration: float, memory_before: int, memory_after: int):
        self._operation = operation
        self._duration = duration
        self._memory_before = memory_before
        self._memory_after = memory_after
        self._timestamp = time.time()

    @property
    def operation(self) -> str:
        return self._operation

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def memory_delta(self) -> int:
        return self._memory_after - self._memory_before

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self._operation,
            "duration": self._duration,
            "memory_before": self._memory_before,
            "memory_after": self._memory_after,
            "memory_delta": self.memory_delta,
            "timestamp": self._timestamp,
        }


class MemoryProfiler:
    """Performance profiler for the memory subsystem."""

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._samples: list[ProfileSample] = []
        self._operation_totals: dict[str, float] = {}
        self._operation_counts: dict[str, int] = {}

    @property
    def enabled(self) -> bool:
        return self._enabled

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def profile(self, operation: str) -> Callable[[], None]:
        if not self._enabled:
            return lambda: None
        before = time.time()
        mem_before = self._estimate_memory()

        def finish() -> None:
            duration = time.time() - before
            mem_after = self._estimate_memory()
            sample = ProfileSample(operation, duration, mem_before, mem_after)
            self._samples.append(sample)
            self._operation_totals[operation] = self._operation_totals.get(operation, 0.0) + duration
            self._operation_counts[operation] = self._operation_counts.get(operation, 0) + 1
            if len(self._samples) > 10000:
                self._samples = self._samples[-5000:]

        return finish

    async def aprofile(self, operation: str) -> Callable[[], None]:
        return self.profile(operation)

    def _estimate_memory(self) -> int:
        import sys

        return sys.getsizeof(self._samples)

    def get_operation_stats(self, operation: str) -> dict[str, Any]:
        count = self._operation_counts.get(operation, 0)
        total = self._operation_totals.get(operation, 0.0)
        return {
            "operation": operation,
            "count": count,
            "total_time": total,
            "avg_time": total / count if count > 0 else 0.0,
        }

    def summary(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "total_samples": len(self._samples),
            "operations": {
                op: {
                    "count": self._operation_counts.get(op, 0),
                    "total_time": self._operation_totals.get(op, 0.0),
                }
                for op in set(list(self._operation_counts.keys()) + list(self._operation_totals.keys()))
            },
        }

    def clear(self) -> None:
        self._samples.clear()
        self._operation_totals.clear()
        self._operation_counts.clear()
