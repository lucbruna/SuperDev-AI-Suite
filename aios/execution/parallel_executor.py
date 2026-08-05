"""ParallelExecutor: deterministic simulation of bounded parallel execution."""
from __future__ import annotations

from typing import Any, Callable


class ParallelExecutor:
    """Runs independent work units with bounded-worker semantics.

    Work is executed in submission (dict insertion) order, so results and
    failure ordering are fully deterministic. A failure aborts the batch.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max(1, int(max_workers))
        self._stats: dict[str, int] = {"submitted": 0, "completed": 0, "failed": 0}

    def execute_many(self, fns: dict[str, Callable[[], Any]]) -> dict[str, Any]:
        self._stats["submitted"] += len(fns)
        results: dict[str, Any] = {}
        for key in fns:
            try:
                results[key] = fns[key]()
                self._stats["completed"] += 1
            except Exception as exc:
                self._stats["failed"] += 1
                raise
        return results

    def stats(self) -> dict[str, Any]:
        return dict(self._stats)
