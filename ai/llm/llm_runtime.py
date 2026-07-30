from __future__ import annotations

from typing import Any

from .llm_executor import LLMExecutor
from .llm_logger import LLMLogger
from .llm_metrics import LLMMetricsCollector
from .llm_registry import LLMRegistry


class LLMRuntime:
    """Runtime environment for LLM operations."""

    def __init__(
        self,
        registry: LLMRegistry,
        executor: LLMExecutor,
        metrics: LLMMetricsCollector,
        logger: LLMLogger,
    ) -> None:
        self._registry = registry
        self._executor = executor
        self._metrics = metrics
        self._logger = logger
        self._active_requests: dict[str, dict[str, Any]] = {}

    @property
    def registry(self) -> LLMRegistry:
        return self._registry

    @property
    def executor(self) -> LLMExecutor:
        return self._executor

    @property
    def metrics(self) -> LLMMetricsCollector:
        return self._metrics

    @property
    def logger(self) -> LLMLogger:
        return self._logger

    def track_request(self, request_id: str, provider: str, model: str) -> None:
        self._active_requests[request_id] = {
            "provider": provider,
            "model": model,
            "status": "running",
        }
        self._logger.info(provider, f"Tracking request {request_id}")

    def complete_request(self, request_id: str) -> None:
        if request_id in self._active_requests:
            self._active_requests[request_id]["status"] = "completed"

    def fail_request(self, request_id: str, error: str) -> None:
        if request_id in self._active_requests:
            self._active_requests[request_id]["status"] = "failed"
            self._active_requests[request_id]["error"] = error

    @property
    def active_request_count(self) -> int:
        return len(self._active_requests)

    def get_status(self) -> dict[str, Any]:
        return {
            "active_providers": self._registry.active_providers,
            "active_requests": self.active_request_count,
            "metrics": self._metrics.to_dict(),
        }

    async def shutdown(self) -> None:
        self._logger.info("runtime", "Shutting down LLM runtime")
        for provider_name in self._registry.list_names():
            provider = self._registry.get(provider_name)
            if provider:
                await provider.cleanup()
