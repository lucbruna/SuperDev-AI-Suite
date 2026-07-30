from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from .llm_models import LLMMetrics


class LLMMetricsCollector:
    """Collects and aggregates LLM operation metrics."""

    def __init__(self) -> None:
        self._metrics: list[LLMMetrics] = []
        self._provider_totals: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    def record(
        self,
        provider: str = "",
        model: str = "",
        latency_ms: float = 0.0,
        tokens_prompt: int = 0,
        tokens_completion: int = 0,
        cost_usd: float = 0.0,
        success: bool = True,
        error: str = "",
    ) -> None:
        m = LLMMetrics(
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            cost_usd=cost_usd,
            success=success,
            error=error,
        )
        self._metrics.append(m)

        self._provider_totals[provider]["requests"] += 1
        self._provider_totals[provider]["latency_ms"] += latency_ms
        self._provider_totals[provider]["tokens"] += tokens_prompt + tokens_completion
        self._provider_totals[provider]["cost_usd"] += cost_usd
        if not success:
            self._provider_totals[provider]["errors"] += 1

    @property
    def total_requests(self) -> int:
        return len(self._metrics)

    @property
    def total_cost(self) -> float:
        return sum(m.cost_usd for m in self._metrics)

    @property
    def total_tokens(self) -> int:
        return sum(m.tokens_prompt + m.tokens_completion for m in self._metrics)

    @property
    def error_rate(self) -> float:
        if not self._metrics:
            return 0.0
        errors = sum(1 for m in self._metrics if not m.success)
        return errors / len(self._metrics)

    def get_provider_stats(self, provider: str) -> dict[str, Any]:
        return dict(self._provider_totals.get(provider, {}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "error_rate": self.error_rate,
            "providers": {k: dict(v) for k, v in self._provider_totals.items()},
        }

    def reset(self) -> None:
        self._metrics.clear()
        self._provider_totals.clear()
