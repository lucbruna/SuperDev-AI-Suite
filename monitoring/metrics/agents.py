from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class AgentMetrics:
    """Metrics collector for AI agent execution."""

    def __init__(self) -> None:
        self._invocations: int = 0
        self._errors: int = 0
        self._total_tokens: int = 0
        self._total_duration_ms: float = 0.0

    def record_invocation(self, agent: str, duration_ms: float, tokens: int = 0, success: bool = True) -> list[MetricSample]:
        self._invocations += 1
        self._total_duration_ms += duration_ms
        self._total_tokens += tokens
        if not success:
            self._errors += 1
        return [
            MetricSample("agent_invocations_total", 1.0, labels={"agent": agent}, metric_type=MetricType.COUNTER),
            MetricSample("agent_duration_ms", duration_ms, labels={"agent": agent}, metric_type=MetricType.HISTOGRAM),
            MetricSample("agent_tokens_total", float(tokens), labels={"agent": agent}, metric_type=MetricType.COUNTER),
            MetricSample("agent_errors_total", 0.0 if success else 1.0, labels={"agent": agent}, metric_type=MetricType.COUNTER),
        ]

    def snapshot(self) -> dict[str, Any]:
        return {
            "invocations": self._invocations,
            "errors": self._errors,
            "total_tokens": self._total_tokens,
            "avg_duration_ms": round(self._total_duration_ms / self._invocations, 2) if self._invocations else 0.0,
        }


__all__ = ["AgentMetrics"]
