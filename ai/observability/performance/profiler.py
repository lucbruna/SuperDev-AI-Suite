"""Performance profiler."""

from __future__ import annotations

import time
from typing import Any


class Profiler:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._completed: list[dict[str, Any]] = []

    def start_session(self, name: str) -> str:
        import uuid

        session_id = str(uuid.uuid4())[:8]
        self._sessions[session_id] = {"name": name, "start_time": time.time(), "marks": []}
        return session_id

    def add_mark(self, session_id: str, label: str) -> bool:
        session = self._sessions.get(session_id)
        if session:
            session["marks"].append({"label": label, "time": time.time()})
            return True
        return False

    def end_session(self, session_id: str) -> dict[str, Any]:
        session = self._sessions.pop(session_id, None)
        if not session:
            return {"error": "session_not_found"}
        session["end_time"] = time.time()
        session["duration_ms"] = (session["end_time"] - session["start_time"]) * 1000
        self._completed.append(session)
        return session

    def get_results(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._completed[-limit:]

    def active_sessions(self) -> int:
        return len(self._sessions)
