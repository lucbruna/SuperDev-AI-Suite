"""Session management."""
from __future__ import annotations
from typing import Any, Dict, List
import uuid, time

class SessionManager:
    def __init__(self, timeout: int = 1800) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._timeout = timeout
    def create(self, user_id: str, ip: str = "") -> Dict[str, Any]:
        sid = str(uuid.uuid4())[:12]
        self._sessions[sid] = {"session_id": sid, "user_id": user_id, "ip": ip, "created_at": time.time(), "last_activity": time.time(), "active": True}
        return self._sessions[sid]
    def get(self, session_id: str) -> Dict[str, Any] | None:
        s = self._sessions.get(session_id)
        if s and s["active"] and (time.time() - s["last_activity"]) < self._timeout:
            s["last_activity"] = time.time()
            return s
        return None
    def invalidate(self, session_id: str) -> bool:
        if session_id in self._sessions:
            self._sessions[session_id]["active"] = False
            return True
        return False
    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if s.get("active"))
