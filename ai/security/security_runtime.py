"""Security runtime for managing active security sessions."""
from __future__ import annotations

import time
from typing import Any


class SecurityRuntime:
    """Manages active security sessions and runtime state."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._active_tokens: dict[str, str] = {}

    def create_session(self, user_id: str, ip_address: str = "",
                       extra: dict[str, Any] | None = None) -> dict[str, Any]:
        import uuid
        session_id = str(uuid.uuid4())[:12]
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "ip_address": ip_address,
            "created_at": time.time(),
            "last_activity": time.time(),
            "active": True,
            **(extra or {}),
        }
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    def invalidate_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            self._sessions[session_id]["active"] = False
            return True
        return False

    def register_token(self, token: str, user_id: str) -> None:
        self._active_tokens[token] = user_id

    def validate_token(self, token: str) -> str | None:
        return self._active_tokens.get(token)

    def revoke_token(self, token: str) -> bool:
        if token in self._active_tokens:
            del self._active_tokens[token]
            return True
        return False

    def get_active_sessions(self) -> list[dict[str, Any]]:
        return [s for s in self._sessions.values() if s.get("active")]

    def cleanup_expired(self, timeout_seconds: int = 1800) -> int:
        now = time.time()
        expired = 0
        for _sid, session in self._sessions.items():
            if session.get("active") and (now - session["last_activity"]) > timeout_seconds:
                session["active"] = False
                expired += 1
        return expired

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": len(self.get_active_sessions()),
            "active_tokens": len(self._active_tokens),
        }
