from __future__ import annotations

from .reasoning_context import ReasoningContext
from .reasoning_engine import ReasoningEngine
from .reasoning_models import ReasoningResult
from .reasoning_profiler import ReasoningProfiler


class ReasoningExecutor:
    """Executes reasoning operations with profiling and error handling."""

    def __init__(self, engine: ReasoningEngine | None = None):
        self._engine = engine or ReasoningEngine()
        self._profiler = ReasoningProfiler()

    async def execute(self, context: ReasoningContext) -> ReasoningResult:
        self._profiler.start("reason")
        try:
            result = await self._engine.reason(context)
            elapsed = self._profiler.stop("reason")
            result.metadata["duration_ms"] = elapsed
            return result
        except Exception:
            self._profiler.stop("reason")
            raise

    async def execute_batch(self, contexts: list[ReasoningContext]) -> list[ReasoningResult]:
        results: list[ReasoningResult] = []
        for ctx in contexts:
            result = await self.execute(ctx)
            results.append(result)
        return results
