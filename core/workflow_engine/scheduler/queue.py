from __future__ import annotations

import asyncio


class ExecutionQueue:
    def __init__(self):
        self._queue: asyncio.PriorityQueue[tuple[int, int, str]] = asyncio.PriorityQueue()
        self._counter = 0

    async def enqueue(self, workflow_id: str, priority: int = 0) -> None:
        self._counter += 1
        await self._queue.put((priority, self._counter, workflow_id))

    async def dequeue(self) -> str | None:
        try:
            _, _, workflow_id = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            return workflow_id
        except (TimeoutError, asyncio.CancelledError):
            return None

    async def peek(self) -> str | None:
        try:
            _, _, workflow_id = self._queue.get_nowait()
            await self._queue.put((0, self._counter, workflow_id))
            return workflow_id
        except asyncio.QueueEmpty:
            return None

    def size(self) -> int:
        return self._queue.qsize()

    def is_empty(self) -> bool:
        return self._queue.empty()
