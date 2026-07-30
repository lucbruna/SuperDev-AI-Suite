from __future__ import annotations

import contextvars
from datetime import UTC, datetime
from typing import Any

_request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
_session_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("session_id", default=None)
_user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)
_metadata_var: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar("metadata", default={})


class AIContext:
    """Global AI context for request correlation."""

    @staticmethod
    def get_request_id() -> str | None:
        return _request_id_var.get()

    @staticmethod
    def set_request_id(request_id: str) -> None:
        _request_id_var.set(request_id)

    @staticmethod
    def get_session_id() -> str | None:
        return _session_id_var.get()

    @staticmethod
    def set_session_id(session_id: str) -> None:
        _session_id_var.set(session_id)

    @staticmethod
    def get_user_id() -> str | None:
        return _user_id_var.get()

    @staticmethod
    def set_user_id(user_id: str) -> None:
        _user_id_var.set(user_id)

    @staticmethod
    def get_metadata() -> dict[str, Any]:
        return _metadata_var.get()

    @staticmethod
    def set_metadata(metadata: dict[str, Any]) -> None:
        current = _metadata_var.get()
        current.update(metadata)
        _metadata_var.set(current)

    @staticmethod
    def clear() -> None:
        """Clear all context variables."""
        _request_id_var.set(None)
        _session_id_var.set(None)
        _user_id_var.set(None)
        _metadata_var.set({})

    @staticmethod
    def snapshot() -> dict[str, Any]:
        """Capture current context as a dictionary."""
        return {
            "request_id": _request_id_var.get(),
            "session_id": _session_id_var.get(),
            "user_id": _user_id_var.get(),
            "metadata": dict(_metadata_var.get()),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @staticmethod
    def restore(snapshot: dict[str, Any]) -> None:
        """Restore context from a snapshot."""
        _request_id_var.set(snapshot.get("request_id"))
        _session_id_var.set(snapshot.get("session_id"))
        _user_id_var.set(snapshot.get("user_id"))
        _metadata_var.set(snapshot.get("metadata", {}))

    def __enter__(self) -> AIContext:
        return self

    def __exit__(self, *args: Any) -> None:
        self.clear()
