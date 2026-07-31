from __future__ import annotations

import time
from typing import Any


class ReasoningTrace:
    """A trace of a reasoning operation."""

    def __init__(self, trace_id: str, reasoning_type: str, input_summary: str, output_summary: str, details: dict[str, Any] | None = None):
        self._trace_id = trace_id
        self._reasoning_type = reasoning_type
        self._input_summary = input_summary
        self._output_summary = output_summary
        self._details = details or {}
        self._timestamp = time.time()

    @property
    def trace_id(self) -> str:
        return self._trace_id

    @property
    def reasoning_type(self) -> str:
        return self._reasoning_type

    @property
    def input_summary(self) -> str:
        return self._input_summary

    @property
    def output_summary(self) -> str:
        return self._output_summary

    @property
    def details(self) -> dict[str, Any]:
        return dict(self._details)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self._trace_id,
            "reasoning_type": self._reasoning_type,
            "input": self._input_summary,
            "output": self._output_summary,
            "timestamp": self._timestamp,
        }


class ReasoningHistory:
    """History of reasoning traces."""

    def __init__(self):
        self._traces: list[ReasoningTrace] = []
        self._counter: int = 0

    @property
    def count(self) -> int:
        return len(self._traces)

    def record(self, reasoning_type: str, input_summary: str, output_summary: str, details: dict[str, Any] | None = None) -> ReasoningTrace:
        self._counter += 1
        trace = ReasoningTrace(f"trace_{self._counter}", reasoning_type, input_summary, output_summary, details)
        self._traces.append(trace)
        return trace

    def get_recent(self, count: int = 50) -> list[ReasoningTrace]:
        return list(self._traces[-count:])

    def get_by_type(self, reasoning_type: str) -> list[ReasoningTrace]:
        return [t for t in self._traces if t.reasoning_type == reasoning_type]

    def clear(self) -> None:
        self._traces.clear()
