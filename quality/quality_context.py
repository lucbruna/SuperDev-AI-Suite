from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any

_current_run_id: ContextVar[str] = ContextVar("_quality_run_id", default="")
_current_target: ContextVar[str] = ContextVar("_quality_target", default="")
_current_gate_id: ContextVar[str] = ContextVar("_quality_gate_id", default="")


class QualityContext:
    """Request-scoped context for quality operations.

    Uses ``ContextVar`` for async-safe per-task propagation.
    """

    @staticmethod
    def get_run_id() -> str:
        return _current_run_id.get()

    @staticmethod
    def set_run_id(run_id: str) -> None:
        _current_run_id.set(run_id)

    @staticmethod
    def generate_run_id() -> str:
        rid = uuid.uuid4().hex
        _current_run_id.set(rid)
        return rid

    @staticmethod
    def get_target() -> str:
        return _current_target.get()

    @staticmethod
    def set_target(target: str) -> None:
        _current_target.set(target)

    @staticmethod
    def get_gate_id() -> str:
        return _current_gate_id.get()

    @staticmethod
    def set_gate_id(gate_id: str) -> None:
        _current_gate_id.set(gate_id)

    @staticmethod
    def snapshot() -> dict[str, str]:
        return {
            "run_id": _current_run_id.get(),
            "target": _current_target.get(),
            "gate_id": _current_gate_id.get(),
        }

    @staticmethod
    def to_dict() -> dict[str, Any]:
        return QualityContext.snapshot()


__all__ = ["QualityContext"]
