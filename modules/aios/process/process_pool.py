"""Process pool — managed pool of worker processes."""
from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from modules.aios import get_kernel_logger, get_kernel_metrics
from modules.aios.process.acl import require_process_action
from modules.aios.process.process_manager import ProcessManager, ProcessInfo


@dataclass
class PoolWorker:
    """A worker in the process pool."""
    pid: int
    info: ProcessInfo
    busy: bool = False
    current_task: Any = None


class ProcessPool:
    """Pool of reusable worker processes."""

    def __init__(self, max_workers: int = 4) -> None:
        self._max_workers = max_workers
        self._workers: list[PoolWorker] = []
        self._queue: deque[tuple[Callable[..., Awaitable[Any]], tuple, dict, asyncio.Future]] = deque()
        self._manager = ProcessManager()
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()
        self._running = False

    async def start(self) -> None:
        """Start the pool workers."""
        require_process_action("pool_start")
        self._running = True
        for _ in range(self._max_workers):
            await self._spawn_worker()
        self._logger.log("process", f"pool started with {self._max_workers} workers")
        self._metrics.record_timing("process.pool_start", 0)

    async def _spawn_worker(self) -> None:
        """Spawn a new idle worker."""
        # Workers are just placeholder processes that wait for tasks
        info = await self._manager.spawn(["sleep", "3600"])  # Long-running placeholder
        worker = PoolWorker(pid=info.pid, info=info)
        self._workers.append(worker)

    async def submit(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Submit a task to the pool."""
        require_process_action("pool_submit")
        if not self._running:
            await self.start()

        # Find idle worker
        for worker in self._workers:
            if not worker.busy:
                worker.busy = True
                worker.current_task = (func, args, kwargs)
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    worker.busy = False
                    worker.current_task = None

        # Queue if all busy
        future = asyncio.get_event_loop().create_future()
        self._queue.append((func, args, kwargs, future))
        return await future

    async def shutdown(self) -> None:
        """Shutdown all workers."""
        require_process_action("pool_shutdown")
        self._running = False
        for worker in self._workers:
            await self._manager.terminate(worker.pid, force=True)
        self._workers.clear()
        self._logger.log("process", "pool shutdown")


__all__ = ["ProcessPool", "PoolWorker"]
