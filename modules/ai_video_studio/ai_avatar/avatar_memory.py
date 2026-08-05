"""Avatar memory — remembers per-actor preferences and session state."""
from __future__ import annotations

from typing import Any


class AvatarMemory:
    """In-memory preference store keyed by actor id (and project when given)."""

    def __init__(self) -> None:
        self._prefs: dict[str, dict[str, Any]] = {}
        self._sessions: dict[str, dict[str, Any]] = {}

    def remember(self, actor_id: str, prefs: dict[str, Any]) -> None:
        entry = self._prefs.setdefault(actor_id, {})
        entry.update(prefs)

    def recall(self, actor_id: str) -> dict[str, Any]:
        return dict(self._prefs.get(actor_id, {}))

    def start_session(self, session_id: str, **meta: Any) -> str:
        self._sessions[session_id] = {"id": session_id, **meta, "frames": 0}
        return session_id

    def end_session(self, session_id: str, frames: int = 0) -> dict[str, Any] | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        session["frames"] = frames
        return session

    def sessions(self) -> list[dict[str, Any]]:
        return [dict(s) for s in self._sessions.values()]


_avatar_memory: AvatarMemory | None = None


def get_avatar_memory() -> AvatarMemory:
    global _avatar_memory
    if _avatar_memory is None:
        _avatar_memory = AvatarMemory()
    return _avatar_memory
