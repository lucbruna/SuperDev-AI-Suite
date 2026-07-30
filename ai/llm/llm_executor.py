from __future__ import annotations

import time
import uuid
from typing import Any, AsyncIterator

from .llm_interfaces import ILLMExecutor, ILLMProvider
from .llm_logger import LLMLogger
from .llm_metrics import LLMMetricsCollector
from .llm_registry import LLMRegistry


class LLMExecutor(ILLMExecutor):
    """Executes LLM requests with validation, metrics, and logging."""

    def __init__(self, registry: LLMRegistry, metrics: LLMMetricsCollector, logger: LLMLogger) -> None:
        self._registry = registry
        self._metrics = metrics
        self._logger = logger

    async def execute(self, provider: str, prompt: str, **kwargs: Any) -> dict[str, Any]:
        prov = self._registry.get(provider)
        if prov is None:
            return {"success": False, "error": f"Unknown provider: {provider}"}

        execution_id = str(uuid.uuid4())
        start = time.time()

        try:
            self._logger.info(provider, f"Starting execution {execution_id}")
            result = await prov.generate(prompt, **kwargs)
            duration = time.time() - start

            self._metrics.record(
                provider=provider,
                model=prov.model(),
                latency_ms=round(duration * 1000, 2),
                tokens_prompt=result.get("tokens_prompt", 0),
                tokens_completion=result.get("tokens_completion", 0),
                success=result.get("success", True),
            )

            result["execution_id"] = execution_id
            result["duration_ms"] = round(duration * 1000, 2)
            self._logger.info(provider, f"Completed {execution_id}", duration_ms=result["duration_ms"])
            return result

        except Exception as e:
            duration = time.time() - start
            self._metrics.record(provider=provider, success=False, error=str(e))
            self._logger.error(provider, f"Execution failed: {e}")
            return {"success": False, "error": str(e), "execution_id": execution_id}

    async def execute_stream(
        self, provider: str, prompt: str, **kwargs: Any
    ) -> AsyncIterator[dict[str, Any]]:
        prov = self._registry.get(provider)
        if prov is None:
            yield {"success": False, "error": f"Unknown provider: {provider}"}
            return

        try:
            async for chunk in prov.generate_stream(prompt, **kwargs):
                yield chunk
        except Exception as e:
            yield {"success": False, "error": str(e)}

    async def execute_batch(
        self, tasks: list[tuple[str, str, dict[str, Any]]]
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for provider, prompt, kwargs in tasks:
            result = await self.execute(provider, prompt, **kwargs)
            results.append(result)
        return results
