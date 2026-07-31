from __future__ import annotations

import logging
import threading
from typing import Any, Callable


class CollaborationSession:
    """Collaborative editing session with presence tracking."""

    def __init__(self, session_id: str) -> None:
        self._log = logging.getLogger("superdev.frontend.realtime.collab")
        self.session_id = session_id
        self._clients: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._listeners: list[Callable[[str, Any], None]] = []

    def join(self, client_id: str, name: str = "") -> None:
        with self._lock:
            self._clients[client_id] = {"name": name, "joined_at": 0.0}
        self._notify("client_joined", {"client_id": client_id})

    def leave(self, client_id: str) -> bool:
        with self._lock:
            removed = self._clients.pop(client_id, None) is not None
        if removed:
            self._notify("client_left", {"client_id": client_id})
        return removed

    def presence(self) -> list[dict[str, Any]]:
        with self._lock:
            return [{"client_id": cid, **info} for cid, info in self._clients.items()]

    def on_event(self, listener: Callable[[str, Any], None]) -> None:
        self._listeners.append(listener)

    def _notify(self, kind: str, data: Any) -> None:
        for listener in list(self._listeners):
            listener(kind, data)


class Collaboration:
    """Manages collaboration sessions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.realtime.collab")
        self._sessions: dict[str, CollaborationSession] = {}

    def create_session(self, session_id: str) -> CollaborationSession:
        session = CollaborationSession(session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> CollaborationSession:
        if session_id not in self._sessions:
            raise KeyError(f"unknown collaboration session: {session_id}")
        return self._sessions[session_id]

    def list_sessions(self) -> list[str]:
        return list(self._sessions)

    def close_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None
