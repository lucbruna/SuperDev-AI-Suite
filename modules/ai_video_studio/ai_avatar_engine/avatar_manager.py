"""Avatar manager — lifecycle management for avatar sessions and profiles."""
from __future__ import annotations

import time
from typing import Any

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile
from modules.ai_video_studio.ai_avatar_engine.avatar_registry import get_avatar_registry


class AvatarManager:
    """Owns the profile registry and tracks active avatar sessions."""

    def __init__(self) -> None:
        self.registry = get_avatar_registry()
        self._sessions: dict[str, dict[str, Any]] = {}

    # ── profiles ──────────────────────────────────────────────────
    def register(self, profile: AvatarProfile) -> bool:
        return self.registry.add_profile(profile)

    def get(self, profile_id: str) -> AvatarProfile:
        return self.registry.get_profile(profile_id)

    def list(self, **filters: Any) -> list[AvatarProfile]:
        return self.registry.list_profiles(**filters)

    def unregister(self, profile_id: str) -> bool:
        return self.registry.remove_profile(profile_id)

    # ── sessions ──────────────────────────────────────────────────
    def start_session(self, profile_id: str, *, session_id: str | None = None,
                      **meta: Any) -> dict[str, Any]:
        profile = self.get(profile_id)
        sid = session_id or f"session_{int(time.time() * 1000)}"
        self._sessions[sid] = {
            "id": sid, "profile_id": profile.id, "started": round(time.time(), 3),
            "frames": 0, "duration_ms": 0.0, **meta,
        }
        return self._sessions[sid]

    def end_session(self, session_id: str, *, frames: int = 0, duration_ms: float = 0.0) -> dict[str, Any] | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        session["frames"] = frames
        session["duration_ms"] = duration_ms
        session["ended"] = round(time.time(), 3)
        return session

    def sessions(self) -> list[dict[str, Any]]:
        return [dict(s) for s in self._sessions.values()]

    def session(self, session_id: str) -> dict[str, Any] | None:
        s = self._sessions.get(session_id)
        return dict(s) if s else None


_avatar_manager: AvatarManager | None = None


def get_avatar_manager() -> AvatarManager:
    global _avatar_manager
    if _avatar_manager is None:
        _avatar_manager = AvatarManager()
    return _avatar_manager
