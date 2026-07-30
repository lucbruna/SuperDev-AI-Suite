from __future__ import annotations

import time
from typing import Any


class Tracing:
    """Manages distributed tracing spans."""

    def __init__(self) -> None:
        self._spans: dict[str, dict[str, Any]] = {}
        self._traces: dict[str, list[str]] = {}

    def start_span(self, name: str, trace_id: str = "default") -> str:
        self._spans[name] = {"name": name, "trace_id": trace_id, "start": time.time(), "end": None}
        if trace_id not in self._traces:
            self._traces[trace_id] = []
        self._traces[trace_id].append(name)
        return name

    def end_span(self, name: str) -> bool:
        if name in self._spans:
            self._spans[name]["end"] = time.time()
            return True
        return False

    def get_trace(self, trace_id: str) -> list[str] | None:
        return self._traces.get(trace_id)

    @property
    def span_count(self) -> int:
        return len(self._spans)

    def to_dict(self) -> dict[str, Any]:
        return {
            "spans": list(self._spans.values()),
            "traces": {k: v for k, v in self._traces.items()},
            "span_count": self.span_count,
        }
