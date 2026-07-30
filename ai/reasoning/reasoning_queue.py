from __future__ import annotations

import asyncio
from typing import Any

from .reasoning_context import ReasoningContext
from .reasoning_executor import ReasoningExecutor
from .reasoning_models import ReasoningResult


class ReasoningQueue:
    """Queue for managing pending reasoning tasks."""

    def __init__(self, executor: ReasoningExecutor | None = None):
        self._executor = executor or ReasoningExecutor()
        self._queue: asyncio.Queue[ReasoningContext] = asyncio.Queue()
        self._results: dict[str, ReasoningResult] = {}

    async def enqueue(self, context: ReasoningContext) -> None:
        await self._queue.put(context)

    async def process_next(self) -> ReasoningResult | None:
        if self._queue.empty():
            return None
        context = await self._queue.get()
        result = await self._executor.execute(context)
        self._results[context.context_id] = result
        return result

    async def process_all(self) -> list[ReasoningResult]:
        results: list[ReasoningResult] = []
        while not self._queue.empty():
            result = await self.process_next()
            if result:
                results.append(result)
        return results

    def pending(self) -> int:
        return self._queue.qsize()

    def get_result(self, context_id: str) -> ReasoningResult | None:
        return self._results.get(context_id)
