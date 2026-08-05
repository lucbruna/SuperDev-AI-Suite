"""AIOS Session Runtime — session-scoped state and execution.

Sessions group related executions (conversation, agent run, workflow)
with their own state store, so parallel work stays isolated.
"""

from __future__ import annotations

import inspect
import uuid
from typing import Any

from .runtime import BaseRuntime, RuntimeCallable


class SessionRuntime(BaseRuntime):
    """Run targets inside a named session with scoped state."""

    kind = "session"

    def __init__(self, name: str = "session-runtime") -> None:
        super().__init__(name)
        self._sessions: dict[str, dict[str, Any]] = {}

    def create_session(self, session_id: str | None = None, **initial: Any) -> str:
        sid = session_id or f"session-{uuid.uuid4().hex[:10]}"
        self._sessions[sid] = dict(initial)
        return sid

    def get_state(self, session_id: str) -> dict[str, Any]:
        return self._sessions.get(session_id, {})

    def set_state(self, session_id: str, **values: Any) -> None:
        self._sessions.setdefault(session_id, {}).update(values)

    def close_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    async def run(self, target: RuntimeCallable, context: dict[str, Any]) -> dict[str, Any]:
        session_id = context.get("session_id")
        if session_id is None:
            session_id = self.create_session()
            context["session_id"] = session_id
        self._sessions.setdefault(session_id, {})
        try:
            result = target(context)
            if inspect.isawaitable(result):
                result = await result
            return {"ok": True, "session_id": session_id, "result": result}
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "session_id": session_id,
                "error": f"{type(exc).__name__}: {exc}",
                "result": None,
            }

    def snapshot(self) -> dict[str, Any]:
        return {"sessions": sorted(self._sessions.keys())}
