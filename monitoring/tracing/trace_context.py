from __future__ import annotations

import contextvars
from typing import Any

from ..monitoring_models import Span, Trace

trace_var: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "trace_context", default={}
)


class TraceContext:
    """Context manager for trace propagation using ContextVar."""

    @staticmethod
    def set(trace_id: str, span_id: str) -> None:
        trace_var.set({"trace_id": trace_id, "span_id": span_id})

    @staticmethod
    def get() -> dict[str, Any]:
        return trace_var.get()

    @staticmethod
    def get_trace_id() -> str:
        return trace_var.get().get("trace_id", "")

    @staticmethod
    def get_span_id() -> str:
        return trace_var.get().get("span_id", "")

    @staticmethod
    def clear() -> None:
        trace_var.set({})

    @staticmethod
    def in_span(trace_id: str, span_id: str) -> _TraceContextManager:
        return _TraceContextManager(trace_id, span_id)


class _TraceContextManager:
    def __init__(self, trace_id: str, span_id: str) -> None:
        self._trace_id = trace_id
        self._span_id = span_id
        self._previous: dict[str, Any] = {}

    def __enter__(self) -> dict[str, Any]:
        self._previous = trace_var.get()
        trace_var.set({"trace_id": self._trace_id, "span_id": self._span_id})
        return trace_var.get()

    def __exit__(self, *args: object) -> None:
        trace_var.set(self._previous)
