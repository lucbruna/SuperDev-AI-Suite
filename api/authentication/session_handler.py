from __future__ import annotations

import secrets
import time
from typing import Any

from ..api_interfaces import IAPIAuthenticator


class SessionHandler(IAPIAuthenticator):
    """In-memory session management with TTL support."""

    def __init__(self, default_ttl: int = 3600) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._default_ttl = default_ttl

    def create_session(self, user_id: str, metadata: dict[str, Any] | None = None, ttl: int | None = None) -> str:
        session_id = secrets.token_hex(32)
        expires_at = time.time() + (ttl or self._default_ttl)
        self._sessions[session_id] = {
            "user_id": user_id,
            "metadata": metadata or {},
            "created_at": time.time(),
            "expires_at": expires_at,
        }
        return session_id

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if time.time() > session["expires_at"]:
            self.delete_session(session_id)
            return None
        return dict(session)

    def update_session(self, session_id: str, metadata: dict[str, Any]) -> bool:
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session["metadata"].update(metadata)
        return True

    def delete_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def cleanup_expired(self) -> int:
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now > s["expires_at"]]
        for sid in expired:
            self._sessions.pop(sid, None)
        return len(expired)

    def get_active_count(self) -> int:
        self.cleanup_expired()
        return len(self._sessions)

    async def authenticate(self, request: Any) -> dict[str, Any]:
        headers = getattr(request, "headers", {}) if hasattr(request, "headers") else {}
        cookie = headers.get("cookie", "") if isinstance(headers, dict) else ""
        if "session=" in cookie:
            session_id = cookie.split("session=")[1].split(";")[0].strip()
            session = self.get_session(session_id)
            if session:
                return {"authenticated": True, "method": "session", **session}
        return {"authenticated": False, "method": "session", "error": "Invalid or expired session"}

    async def validate_token(self, token: str) -> dict[str, Any]:
        session = self.get_session(token)
        if session:
            return {"valid": True, **session}
        return {"valid": False, "error": "Invalid or expired session"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_sessions": self.get_active_count(),
            "default_ttl": self._default_ttl,
        }
