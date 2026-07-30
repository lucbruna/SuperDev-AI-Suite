from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class LlmMetrics:
    """Metrics for LLM inference (token usage, latency, cost)."""

    def __init__(self) -> None:
        self._prompt_tokens: int = 0
        self._completion_tokens: int = 0
        self._total_latency_ms: float = 0.0
        self._requests: int = 0

    def record_request(self, prompt_tokens: int, completion_tokens: int, latency_ms: float) -> list[MetricSample]:
        self._requests += 1
        self._prompt_tokens += prompt_tokens
        self._completion_tokens += completion_tokens
        self._total_latency_ms += latency_ms
        return [
            MetricSample("llm_requests_total", 1.0, metric_type=MetricType.COUNTER),
            MetricSample("llm_prompt_tokens", float(prompt_tokens), metric_type=MetricType.COUNTER),
            MetricSample("llm_completion_tokens", float(completion_tokens), metric_type=MetricType.COUNTER),
            MetricSample("llm_latency_ms", latency_ms, metric_type=MetricType.HISTOGRAM),
        ]

    def snapshot(self) -> dict[str, Any]:
        return {
            "requests": self._requests,
            "prompt_tokens": self._prompt_tokens,
            "completion_tokens": self._completion_tokens,
            "total_tokens": self._prompt_tokens + self._completion_tokens,
            "avg_latency_ms": round(self._total_latency_ms / self._requests, 2) if self._requests else 0.0,
        }

    def reset(self) -> None:
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_latency_ms = 0.0
        self._requests = 0


__all__ = ["LlmMetrics"]
