from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any


_current_trace_id: ContextVar[str] = ContextVar("_data_trace_id", default="")
_current_batch_id: ContextVar[str] = ContextVar("_data_batch_id", default="")
_current_source: ContextVar[str] = ContextVar("_data_source", default="")


class DataContext:
    """Request-scoped context for data operations.

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
    def get_batch_id() -> str:
        return _current_batch_id.get()

    @staticmethod
    def set_batch_id(batch_id: str) -> None:
        _current_batch_id.set(batch_id)

    @staticmethod
    def get_source() -> str:
        return _current_source.get()

    @staticmethod
    def set_source(source: str) -> None:
        _current_source.set(source)

    @staticmethod
    def snapshot() -> dict[str, str]:
        return {
            "trace_id": _current_trace_id.get(),
            "batch_id": _current_batch_id.get(),
            "source": _current_source.get(),
        }

    @staticmethod
    def to_dict() -> dict[str, Any]:
        return DataContext.snapshot()


__all__ = ["DataContext"]
