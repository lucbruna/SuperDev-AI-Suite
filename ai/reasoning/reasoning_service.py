from __future__ import annotations

from typing import Any

from .reasoning_engine import ReasoningEngine
from .reasoning_context import ReasoningContext
from .reasoning_models import ReasoningResult


class ReasoningService:
    """High-level service interface for the reasoning engine."""

    def __init__(self, engine: ReasoningEngine | None = None):
        self._engine = engine or ReasoningEngine()

    async def analyze(self, query: str, metadata: dict[str, Any] | None = None) -> ReasoningResult:
        context = ReasoningContext(query=query, metadata=metadata or {})
        return await self._engine.reason(context)

    async def decide(self, options: list[str], criteria: dict[str, Any]) -> ReasoningResult:
        context = ReasoningContext(query=" | ".join(options), metadata={"criteria": criteria})
        return await self._engine.reason(context)

    async def validate(self, decision: str, context: ReasoningContext) -> dict[str, Any]:
        return {"valid": True, "confidence": 0.9}
