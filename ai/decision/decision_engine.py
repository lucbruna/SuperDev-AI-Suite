from __future__ import annotations

from typing import Any

from .decision_context import DecisionContext
from .decision_models import DecisionResult
from .decision_selector import DecisionSelector


class DecisionEngine:
    """Main decision-making engine."""

    def __init__(self, selector: DecisionSelector | None = None):
        self._selector = selector or DecisionSelector()

    async def decide(self, context: DecisionContext) -> DecisionResult:
        options = context.options
        if not options:
            return DecisionResult(decision="", confidence=0.0, context_id=context.context_id)
        selected = await self._selector.select(options, context)
        return DecisionResult(
            decision=selected["option"],
            confidence=selected["confidence"],
            context_id=context.context_id,
        )

    async def evaluate(self, context: DecisionContext) -> list[dict[str, Any]]:
        return [
            {"option": opt, "score": 0.5, "confidence": 0.5}
            for opt in context.options
        ]
