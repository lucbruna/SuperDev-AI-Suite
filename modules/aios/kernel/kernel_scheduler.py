"""Kernel scheduler — periodic kernel jobs with a background loop."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable

JobFn = Callable[[], Any]


@dataclass
class _Job:
    name: str
    interval_s: float
    fn: JobFn
    last_run: str | None = None
    runs: int = 0
    last_error: str | None = None


class KernelScheduler:
    """Runs periodic kernel jobs in a background task."""

    def __init__(self) -> None:
        self._jobs: dict[str, _Job] = {}
        self._task: asyncio.Task | None = None
        self._running = False

    def schedule(self, name: str, interval_s: float, fn: JobFn) -> None:
        self._jobs[name] = _Job(name=name, interval_s=max(0.1, float(interval_s)), fn=fn)

    def unschedule(self, name: str) -> bool:
        return self._jobs.pop(name, None) is not None

    def start(self) -> bool:
        if self._running:
            return False
        self._running = True
        self._task = asyncio.get_running_loop().create_task(self._loop())
        return True

    def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            self._task = None

    async def _loop(self) -> None:
        while self._running:
            for job in list(self._jobs.values()):
                try:
                    if asyncio.iscoroutinefunction(job.fn):
                        await job.fn()
                    else:
                        await asyncio.to_thread(job.fn)
                    job.runs += 1
                    job.last_error = None
                except Exception as e:  # noqa: BLE001 — scheduler must keep running
                    job.last_error = str(e)
                finally:
                    job.last_run = datetime.now(UTC).isoformat()
            await asyncio.sleep(1.0)

    def snapshot(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "jobs": [
                {
                    "name": j.name,
                    "interval_s": j.interval_s,
                    "last_run": j.last_run,
                    "runs": j.runs,
                    "last_error": j.last_error,
                }
                for j in self._jobs.values()
            ],
        }


_kernel_scheduler: KernelScheduler | None = None


def get_kernel_scheduler() -> KernelScheduler:
    global _kernel_scheduler
    if _kernel_scheduler is None:
        _kernel_scheduler = KernelScheduler()
    return _kernel_scheduler
