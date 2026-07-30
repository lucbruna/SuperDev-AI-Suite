from __future__ import annotations

from typing import Any

from .inference_cache import InferenceCache
from .inference_metrics import InferenceMetrics
from .inference_repository import InferenceRepository
from .inference_validator import InferenceValidator


class InferenceEngine:
    """Core inference engine coordinating reasoning strategies."""

    def __init__(
        self,
        cache: InferenceCache | None = None,
        metrics: InferenceMetrics | None = None,
        repository: InferenceRepository | None = None,
        validator: InferenceValidator | None = None,
    ):
        self._cache = cache or InferenceCache()
        self._metrics = metrics or InferenceMetrics()
        self._repository = repository or InferenceRepository()
        self._validator = validator or InferenceValidator()
        self._strategies: dict[str, Any] = {}

    def register_strategy(self, name: str, strategy: Any) -> None:
        self._strategies[name] = strategy

    async def infer(self, context: dict[str, Any], strategy: str = "default") -> Any:
        if self._validator:
            context = await self._validator.validate(context)
        engine = self._strategies.get(strategy)
        if not engine:
            raise ValueError(f"Unknown strategy: {strategy}")
        result = await engine.execute(context)
        if self._metrics:
            await self._metrics.record(strategy, result)
        return result

    async def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        for name, engine in self._strategies.items():
            result = await engine.execute(context)
            results.append({"strategy": name, "result": result})
        return results
