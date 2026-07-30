from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any, Callable

from ..database_interfaces import IDatabaseDriver


class JobQueue:
    """Lightweight job queue backed by a database table.

    Useful for async task scheduling without an external broker.
    """

    def __init__(self, driver: IDatabaseDriver, table: str = "_job_queue") -> None:
        self._driver = driver
        self._table = table
        self._running = False
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register(self, job_type: str, handler: Callable[..., Any]) -> None:
        self._handlers[job_type] = handler

    async def enqueue(self, job_type: str, payload: dict[str, Any], delay: float = 0.0) -> str:
        job_id = uuid.uuid4().hex
        run_at = time.time() + delay
        q = (
            f"INSERT INTO {self._table} (id, job_type, payload, status, run_at, created_at) "
            "VALUES (?, ?, ?, 'pending', ?, ?)"
        )
        await self._driver.execute(q, [
            job_id, job_type, json.dumps(payload), run_at, time.time(),
        ])
        return job_id

    async def worker(self, poll_interval: float = 1.0) -> None:
        self._running = True
        while self._running:
            job = await self._dequeue()
            if job is None:
                await asyncio.sleep(poll_interval)
                continue
            job_type = job.get("job_type", "")
            handler = self._handlers.get(job_type)
            if handler is None:
                await self._fail(job["id"], f"No handler for {job_type}")
                continue
            try:
                payload = json.loads(job.get("payload", "{}"))
                if asyncio.iscoroutinefunction(handler):
                    await handler(**payload)
                else:
                    handler(**payload)
                await self._complete(job["id"])
            except Exception as exc:
                await self._fail(job["id"], str(exc))

    async def stop(self) -> None:
        self._running = False

    async def _dequeue(self) -> dict[str, Any] | None:
        q = (
            f"SELECT * FROM {self._table} "
            f"WHERE status = 'pending' AND run_at <= ? "
            f"ORDER BY created_at ASC LIMIT 1"
        )
        rows = await self._driver.execute_query(q, [time.time()])
        if not rows:
            return None
        job = rows[0]
        await self._driver.execute(
            f"UPDATE {self._table} SET status = 'running' WHERE id = ?",
            [job["id"]],
        )
        return job

    async def _complete(self, job_id: str) -> None:
        await self._driver.execute(
            f"UPDATE {self._table} SET status = 'completed' WHERE id = ?",
            [job_id],
        )

    async def _fail(self, job_id: str, error: str) -> None:
        await self._driver.execute(
            f"UPDATE {self._table} SET status = 'failed', error = ? WHERE id = ?",
            [error, job_id],
        )


__all__ = [
    "JobQueue",
]
