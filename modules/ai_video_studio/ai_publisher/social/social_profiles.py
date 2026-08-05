"""Social Profiles — registry of connected social accounts (Volume 7)."""
from __future__ import annotations

import logging
import uuid

logger = logging.getLogger(__name__)

_PLATFORMS = ["youtube", "tiktok", "instagram", "facebook", "linkedin", "x"]


class SocialProfiles:
    """Manage per-platform account profiles and their connection state."""

    def __init__(self) -> None:
        self._profiles: dict[str, dict] = {}

    def add(self, *, platform: str, name: str, handle: str = "", connected: bool = False) -> dict:
        """Register a social profile."""
        if platform.lower() not in _PLATFORMS:
            return {"success": False, "error": f"Unsupported platform '{platform}'"}
        profile_id = uuid.uuid4().hex[:12]
        profile = {
            "id": profile_id,
            "platform": platform.lower(),
            "name": name,
            "handle": handle,
            "connected": bool(connected),
        }
        self._profiles[profile_id] = profile
        return {"success": True, "profile": profile}

    def list(self, *, platform: str | None = None) -> list[dict]:
        profiles = list(self._profiles.values())
        if platform:
            profiles = [p for p in profiles if p["platform"] == platform.lower()]
        return profiles

    def set_connected(self, profile_id: str, connected: bool) -> bool:
        profile = self._profiles.get(profile_id)
        if not profile:
            return False
        profile["connected"] = bool(connected)
        return True

    def stats(self) -> dict[str, int]:
        return {"profiles": len(self._profiles)}


_PROFILES: SocialProfiles | None = None


def get_social_profiles() -> SocialProfiles:
    """Get the module-level singleton profile registry."""
    global _PROFILES
    if _PROFILES is None:
        _PROFILES = SocialProfiles()
    return _PROFILES
