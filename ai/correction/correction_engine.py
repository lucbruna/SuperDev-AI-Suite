from __future__ import annotations

from typing import Any

from .optimization_engine import OptimizationEngine
from .refinement_engine import RefinementEngine
from .retry_engine import RetryEngine
from .rollback_engine import RollbackEngine
from .self_corrector import SelfCorrector


class CorrectionEngine:
    """Core correction engine coordinating correction strategies."""

    def __init__(
        self,
        self_corrector: SelfCorrector | None = None,
        retry: RetryEngine | None = None,
        rollback: RollbackEngine | None = None,
        refinement: RefinementEngine | None = None,
        optimization: OptimizationEngine | None = None,
    ):
        self._self_corrector = self_corrector or SelfCorrector()
        self._retry = retry or RetryEngine()
        self._rollback = rollback or RollbackEngine()
        self._refinement = refinement or RefinementEngine()
        self._optimization = optimization or OptimizationEngine()

    async def correct(self, response: str, error: dict[str, Any]) -> dict[str, Any]:
        corrected = await self._self_corrector.correct(response, error)
        if corrected.get("success"):
            return corrected
        refined = await self._refinement.refine(response, error)
        return refined

    async def recover(self, context: dict[str, Any]) -> dict[str, Any]:
        rollback_result = await self._rollback.rollback(context)
        if rollback_result.get("rolled_back"):
            return await self._retry.retry(context)
        return {"success": False, "error": "Recovery failed"}
