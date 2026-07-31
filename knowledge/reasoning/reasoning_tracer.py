from __future__ import annotations

import logging
from typing import Any


class ReasoningTracer:
    """Records and exports reasoning traces for audit and debugging."""

    def __init__(self, max_traces: int = 200) -> None:
        self._log = logging.getLogger("superdev.knowledge.reasoning.tracer")
        self.max_traces = max(1, max_traces)
        self._traces: list[dict[str, Any]] = []

    def trace(self, operation: str, **details: Any) -> None:
        self._traces.append({"operation": operation, **details})
        if len(self._traces) > self.max_traces:
            self._traces = self._traces[-self.max_traces:]

    def list(self, operation: str | None = None) -> list[dict[str, Any]]:
        if operation is None:
            return list(self._traces)
        return [trace for trace in self._traces if trace.get("operation") == operation]

    def count(self) -> int:
        return len(self._traces)

    def clear(self) -> None:
        self._traces.clear()
