from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable

from backend.utils.uuid_utils import generate_uuid


@dataclass
class ScheduledJob:
    id: str
    name: str
    func: Callable[..., Awaitable[Any]]
    args: tuple = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    interval_seconds: float = 60
    next_run: datetime | None = None
    last_run: datetime | None = None
    enabled: bool = True
    run_count: int = 0


class Scheduler:
    """Simple async task scheduler."""

    def __init__(self):
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._task: asyncio.Task | None = None

    def add_job(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        interval_seconds: float = 60,
        args: tuple = (),
        kwargs: dict[str, Any] | None = None,
    ) -> str:
        job_id = generate_uuid()
        self._jobs[job_id] = ScheduledJob(
            id=job_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            interval_seconds=interval_seconds,
            next_run=datetime.now(timezone.utc),
        )
        return job_id

    def remove_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False

    def enable_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job:
            job.enabled = True
            return True
        return False

    def disable_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job:
            job.enabled = False
            return True
        return False

    def list_jobs(self) -> list[dict[str, Any]]:
        return [
            {
                "id": job.id,
                "name": job.name,
                "interval_seconds": job.interval_seconds,
                "enabled": job.enabled,
                "run_count": job.run_count,
                "last_run": job.last_run.isoformat() if job.last_run else None,
                "next_run": job.next_run.isoformat() if job.next_run else None,
            }
            for job in self._jobs.values()
        ]

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self) -> None:
        while self._running:
            now = datetime.now(timezone.utc)
            for job in list(self._jobs.values()):
                if not job.enabled or not job.next_run:
                    continue
                if now >= job.next_run:
                    try:
                        await job.func(*job.args, **job.kwargs)
                        job.last_run = now
                        job.run_count += 1
                    except Exception:
                        pass
                    from datetime import timedelta
                    job.next_run = now + timedelta(seconds=job.interval_seconds)
            await asyncio.sleep(1)


scheduler = Scheduler()
