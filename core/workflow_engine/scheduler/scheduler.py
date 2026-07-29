from __future__ import annotations

import asyncio
import contextlib
import time
from typing import Any

from croniter import croniter

from workflow_engine.scheduler.queue import ExecutionQueue


class ScheduledJob:
    def __init__(self, workflow_id: str, cron_expr: str):
        self.workflow_id = workflow_id
        self.cron_expr = cron_expr
        self._cron = croniter(cron_expr, time.time())
        self.next_run = self._cron.get_next(float)

    def update_next_run(self) -> float:
        self.next_run = self._cron.get_next(float)
        return self.next_run


class WorkflowScheduler:
    def __init__(self, queue: ExecutionQueue | None = None):
        self._jobs: dict[str, ScheduledJob] = {}
        self._queue = queue or ExecutionQueue()
        self._running = False
        self._task: asyncio.Task | None = None

    def schedule(self, workflow_id: str, cron_expr: str) -> None:
        job = ScheduledJob(workflow_id, cron_expr)
        self._jobs[workflow_id] = job

    def unschedule(self, workflow_id: str) -> None:
        self._jobs.pop(workflow_id, None)

    def list_scheduled(self) -> list[dict[str, Any]]:
        return [
            {"workflow_id": wid, "cron_expr": job.cron_expr, "next_run": job.next_run}
            for wid, job in self._jobs.items()
        ]

    def get_due_workflows(self) -> list[str]:
        now = time.time()
        due = []
        for wid, job in list(self._jobs.items()):
            if job.next_run <= now:
                due.append(wid)
                job.update_next_run()
        return due

    async def start_polling(self, interval: float = 5.0) -> None:
        self._running = True
        self._task = asyncio.create_task(self._poll_loop(interval))

    async def stop_polling(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _poll_loop(self, interval: float) -> None:
        while self._running:
            due = self.get_due_workflows()
            for wid in due:
                await self._queue.enqueue(wid)
            await asyncio.sleep(interval)
