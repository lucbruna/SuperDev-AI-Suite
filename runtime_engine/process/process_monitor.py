from __future__ import annotations

import asyncio
import time
from typing import Awaitable, Callable

from pydantic import BaseModel, Field


class ProcessStats(BaseModel):
    pid: int
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    status: str = "unknown"
    running_time: float = 0.0
    thread_count: int = 0


class ProcessMonitor:
    def __init__(self) -> None:
        self._watchers: dict[int, asyncio.Task] = {}

    async def monitor(self, pid: int) -> ProcessStats:
        import psutil
        try:
            proc = psutil.Process(pid)
            with proc.oneshot():
                cpu = proc.cpu_percent(interval=0.1)
                mem = proc.memory_info().rss / (1024 * 1024)
                status = proc.status()
                created = time.time() - proc.create_time()
                threads = proc.num_threads()
            return ProcessStats(
                pid=pid,
                cpu_percent=cpu,
                memory_mb=mem,
                status=status,
                running_time=created,
                thread_count=threads,
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return ProcessStats(pid=pid, status="not_found")

    async def watch(self, pid: int, callback: Callable[[ProcessStats], Awaitable[None]], interval: float = 2.0) -> asyncio.Task:
        async def _watcher() -> None:
            try:
                while True:
                    stats = await self.monitor(pid)
                    await callback(stats)
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                pass

        task = asyncio.create_task(_watcher())
        self._watchers[pid] = task
        return task

    async def stop_watch(self, pid: int) -> None:
        task = self._watchers.pop(pid, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
