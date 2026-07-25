from __future__ import annotations

import asyncio
import time
from typing import Any

from pydantic import BaseModel, Field


class SessionMetrics(BaseModel):
    session_id: str
    cpu_usage: float = 0.0
    memory_mb: float = 0.0
    running_time: float = 0.0
    process_count: int = 0
    status: str = "unknown"


class RuntimeMonitor:
    def __init__(self, kernel: Any) -> None:
        self._kernel = kernel
        self._monitor_tasks: dict[str, asyncio.Task] = {}

    async def monitor_session(self, session_id: str, interval: float = 5.0) -> asyncio.Task:
        async def _monitor() -> None:
            try:
                while True:
                    session = self._kernel.session_manager.get(session_id)
                    if session is None or session.status in ("completed", "failed", "cancelled", "timeout"):
                        break
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                pass

        task = asyncio.create_task(_monitor())
        self._monitor_tasks[session_id] = task
        return task

    async def stop_monitoring(self, session_id: str) -> None:
        task = self._monitor_tasks.pop(session_id, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def health_check(self) -> dict:
        return await self._kernel.health()

    async def get_metrics(self, session_id: str) -> SessionMetrics:
        session = self._kernel.session_manager.get(session_id)
        if session is None:
            return SessionMetrics(session_id=session_id, status="not_found")
        running_time = 0.0
        if session.started_at:
            end = session.finished_at or __import__("datetime").datetime.utcnow()
            running_time = (end - session.started_at).total_seconds()
        return SessionMetrics(
            session_id=session_id,
            running_time=running_time,
            status=session.status.value,
        )
