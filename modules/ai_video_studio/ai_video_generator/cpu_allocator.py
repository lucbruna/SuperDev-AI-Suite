"""CPU allocator — manage CPU cores/threads for generation workloads."""
from __future__ import annotations

from typing import Any


class CPUAllocator:
    """Tracks CPU worker usage and hands out thread allowances."""

    def __init__(self, total_workers: int | None = None) -> None:
        import os

        self.total_workers = total_workers or max(1, os.cpu_count() or 4)
        self._used = 0

    def allocate(self, threads: int) -> int:
        """Reserve threads, clamped to what is currently available."""
        granted = min(threads, self.total_workers - self._used)
        if granted > 0:
            self._used += granted
        return granted

    def release(self, threads: int) -> None:
        self._used = max(0, self._used - threads)

    def available(self) -> int:
        return self.total_workers - self._used

    def snapshot(self) -> dict[str, Any]:
        return {"total_workers": self.total_workers, "used": self._used, "available": self.available()}


_cpu_allocator: CPUAllocator | None = None


def get_cpu_allocator() -> CPUAllocator:
    global _cpu_allocator
    if _cpu_allocator is None:
        _cpu_allocator = CPUAllocator()
    return _cpu_allocator
