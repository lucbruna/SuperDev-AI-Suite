from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class AIChatEngine:
    """Renders the AI chat page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.ai_chat")
        self._context = context or FrontendContext()
        self._sessions: dict[str, list[dict[str, Any]]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "ai_chat",
            "sessions": len(self._sessions),
        }

    def new_session(self) -> str:
        session_id = f"session-{len(self._sessions) + 1}"
        self._sessions[session_id] = []
        return session_id

    def send(self, session_id: str, message: str) -> dict[str, Any]:
        if session_id not in self._sessions:
            raise KeyError(f"unknown session: {session_id}")
        self._sessions[session_id].append({"role": "user", "content": message, "ts": time.time()})
        reply = {"role": "assistant", "content": f"AI: {message}", "ts": time.time()}
        self._sessions[session_id].append(reply)
        return reply

    def history(self, session_id: str) -> list[dict[str, Any]]:
        return list(self._sessions.get(session_id, []))

    def delete(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None
