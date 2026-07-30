from __future__ import annotations

import asyncio
from typing import Any

from .reasoning_context import ReasoningContext
from .reasoning_engine import ReasoningEngine


class ReasoningScheduler:
    """Schedules reasoning tasks for execution."""

    def __init__(self, engine: ReasoningEngine | None = None):
        self._engine = engine or ReasoningEngine()
        self._tasks: dict[str, asyncio.Task[Any]] = {}

    async def schedule(self, context: ReasoningContext) -> str:
        session_id = context.context_id
        task = asyncio.create_task(self._engine.reason(context))
        self._tasks[session_id] = task
        return session_id

    async def cancel(self, session_id: str) -> bool:
        task = self._tasks.pop(session_id, None)
        if task and not task.done():
            task.cancel()
            return True
        return False

    async def get_result(self, session_id: str) -> Any | None:
        task = self._tasks.get(session_id)
        if task and task.done():
            return task.result()
        return None

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks.values() if not t.done())
