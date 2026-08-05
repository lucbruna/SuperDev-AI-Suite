"""AIOS Kernel Scheduler — periodic and one-shot async jobs.

Schedules coroutine factories on the running event loop. Kept pure
(no persistence); a governance layer may persist schedules later.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Awaitable, Callable

Job = Callable[[], Awaitable[Any]]


class KernelScheduler:
    """Schedule one-shot and interval jobs as asyncio tasks."""

    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task[Any]] = {}
        self._specs: dict[str, dict[str, Any]] = {}

    def _spawn(self, name: str, spec: dict[str, Any]) -> asyncio.Task[Any]:
        task = asyncio.create_task(self._runner(name))
        self._tasks[name] = task
        self._specs[name] = spec
        return task

    async def _runner(self, name: str) -> None:
        spec = self._specs[name]
        job: Job = spec["job"]
        interval: float | None = spec.get("interval")
        try:
            if interval is None:
                await job()
                spec["last_run"] = time.time()
                spec["runs"] = spec.get("runs", 0) + 1
                return
            while True:
                await asyncio.sleep(interval)
                await job()
                spec["last_run"] = time.time()
                spec["runs"] = spec.get("runs", 0) + 1
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            raise
        except Exception as exc:  # noqa: BLE001
            spec["last_error"] = f"{type(exc).__name__}: {exc}"

    def schedule_once(
        self,
        job: Job,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Run ``job`` once when the loop gets control."""
        sched_name = name or f"sched-{uuid.uuid4().hex[:8]}"
        self._spawn(sched_name, {"job": job, "interval": None, "metadata": metadata or {}})
        return sched_name

    def schedule_interval(
        self,
        job: Job,
        interval: float,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Run ``job`` every ``interval`` seconds."""
        sched_name = name or f"sched-{uuid.uuid4().hex[:8]}"
        self._spawn(sched_name, {"job": job, "interval": interval, "metadata": metadata or {}})
        return sched_name

    def cancel(self, name: str) -> bool:
        task = self._tasks.get(name)
        if task is None:
            return False
        task.cancel()
        self._tasks.pop(name, None)
        self._specs.pop(name, None)
        return True

    def shutdown(self) -> None:
        for name in list(self._tasks.keys()):
            self.cancel(name)

    def snapshot(self) -> dict[str, Any]:
        return {
            name: {
                "interval": spec.get("interval"),
                "runs": spec.get("runs", 0),
                "last_run": spec.get("last_run"),
                "last_error": spec.get("last_error"),
            }
            for name, spec in sorted(self._specs.items())
        }
