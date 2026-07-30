from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any


_current_trace_id: ContextVar[str] = ContextVar("_current_trace_id", default="")
_current_span_id: ContextVar[str] = ContextVar("_current_span_id", default="")
_current_correlation_id: ContextVar[str] = ContextVar("_current_correlation_id", default="")


class MonitoringContext:
    """Request-scoped context carrying trace/span/correlation IDs.

    Uses ``ContextVar`` for async-safe per-task propagation.
    """

    @staticmethod
    def get_trace_id() -> str:
        return _current_trace_id.get()

    @staticmethod
    def set_trace_id(trace_id: str) -> None:
        _current_trace_id.set(trace_id)

    @staticmethod
    def generate_trace_id() -> str:
        tid = uuid.uuid4().hex
        _current_trace_id.set(tid)
        return tid

    @staticmethod
    def get_span_id() -> str:
        return _current_span_id.get()

    @staticmethod
    def set_span_id(span_id: str) -> None:
        _current_span_id.set(span_id)

    @staticmethod
    def get_correlation_id() -> str:
        return _current_correlation_id.get()

    @staticmethod
    def set_correlation_id(cid: str) -> None:
        _current_correlation_id.set(cid)

    @staticmethod
    def snapshot() -> dict[str, str]:
        return {
            "trace_id": _current_trace_id.get(),
            "span_id": _current_span_id.get(),
            "correlation_id": _current_correlation_id.get(),
        }


__all__ = ["MonitoringContext"]
