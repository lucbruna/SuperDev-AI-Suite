from __future__ import annotations

from typing import Any

from .decision_context import DecisionContext
from .decision_engine import DecisionEngine
from .decision_models import DecisionResult


class DecisionExecutor:
    """Executes decisions and tracks their outcomes."""

    def __init__(self, engine: DecisionEngine | None = None):
        self._engine = engine or DecisionEngine()
        self._executed: list[dict[str, Any]] = []

    async def execute(self, context: DecisionContext) -> DecisionResult:
        result = await self._engine.decide(context)
        self._executed.append(
            {
                "context_id": context.context_id,
                "decision": result.decision,
                "confidence": result.confidence,
            }
        )
        return result

    async def execute_batch(self, contexts: list[DecisionContext]) -> list[DecisionResult]:
        return [await self.execute(ctx) for ctx in contexts]

    def history(self) -> list[dict[str, Any]]:
        return list(self._executed)

    def clear_history(self) -> None:
        self._executed.clear()
