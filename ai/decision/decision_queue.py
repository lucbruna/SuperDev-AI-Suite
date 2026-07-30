from __future__ import annotations

import asyncio
from typing import Any

from .decision_context import DecisionContext
from .decision_executor import DecisionExecutor
from .decision_models import DecisionResult
from .decision_priority import DecisionPriority


class DecisionQueue:
    """Priority-aware queue for pending decisions."""

    def __init__(self, executor: DecisionExecutor | None = None):
        self._executor = executor or DecisionExecutor()
        self._priority = DecisionPriority()
        self._pending: dict[str, DecisionContext] = {}
        self._results: dict[str, DecisionResult] = {}

    async def enqueue(self, context: DecisionContext, priority: int = 50) -> None:
        self._pending[context.context_id] = context
        self._priority.set(context.context_id, priority)

    async def process_next(self) -> DecisionResult | None:
        ids = self._priority.sorted_ids()
        for ctx_id in ids:
            if ctx_id in self._pending:
                context = self._pending.pop(ctx_id)
                result = await self._executor.execute(context)
                self._results[ctx_id] = result
                return result
        return None

    async def process_all(self) -> list[DecisionResult]:
        results: list[DecisionResult] = []
        while self._pending:
            result = await self.process_next()
            if result:
                results.append(result)
        return results

    def pending_count(self) -> int:
        return len(self._pending)
