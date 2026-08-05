"""User Preferences — per-user preference tracking."""
from __future__ import annotations

from typing import Any


class UserPreferences:
    """Records user preferences keyed by user id."""

    def __init__(self) -> None:
        self._prefs: dict[str, dict[str, Any]] = {}

    def set(self, user_id: str, key: str, value: Any) -> dict[str, Any]:
        self._prefs.setdefault(user_id, {})[key] = value
        return {"user": user_id, "key": key, "value": value}

    def get(self, user_id: str, key: str) -> dict[str, Any]:
        return {"user": user_id, "key": key, "value": self._prefs.get(user_id, {}).get(key)}

    def all(self, user_id: str) -> dict[str, Any]:
        return {"user": user_id, "preferences": dict(self._prefs.get(user_id, {}))}


_user_preferences: UserPreferences | None = None


def get_user_preferences() -> UserPreferences:
    global _user_preferences
    if _user_preferences is None:
        _user_preferences = UserPreferences()
    return _user_preferences
