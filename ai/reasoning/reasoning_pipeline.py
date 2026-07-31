from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .reasoning_context import ReasoningContext
from .reasoning_models import ReasoningResult


class ReasoningPipeline:
    """Pipeline of reasoning stages executed in sequence."""

    def __init__(self):
        self._stages: list[Callable[[ReasoningContext], Any]] = []

    def add_stage(self, stage: Callable[[ReasoningContext], Any], name: str = "") -> None:
        self._stages.append(stage)

    async def run(self, context: ReasoningContext) -> ReasoningResult:
        current = context
        for stage in self._stages:
            result = await stage(current) if callable(stage) else stage(current)
            if isinstance(result, ReasoningResult):
                return result
        return ReasoningResult(decision="pipeline_completed", context_id=context.context_id)

    def clear(self) -> None:
        self._stages.clear()
