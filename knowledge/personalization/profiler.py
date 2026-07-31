from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from .preferences import Preferences


class UserProfiler:
    """Builds a lightweight user profile from interaction signals."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.personalization.profiler")
        self._profiles: dict[str, dict[str, Any]] = {}

    def record_interaction(self, user_id: str, topic: str, weight: float = 1.0) -> None:
        profile = self._profiles.setdefault(user_id, {"interests": Counter(), "count": 0})
        profile["interests"][topic] += weight
        profile["count"] += 1

    def interests(self, user_id: str, top_k: int = 5) -> list[tuple[str, float]]:
        profile = self._profiles.get(user_id)
        if profile is None:
            return []
        return profile["interests"].most_common(top_k)

    def profile(self, user_id: str) -> dict[str, Any]:
        profile = self._profiles.get(user_id)
        if profile is None:
            return {"user_id": user_id, "interests": [], "count": 0}
        return {
            "user_id": user_id,
            "interests": list(profile["interests"].items()),
            "count": profile["count"],
        }

    def apply_preferences(self, user_id: str, preferences: Preferences) -> Preferences:
        interests = self.interests(user_id)
        preferences.set("topics", [topic for topic, _score in interests])
        return preferences

    def clear(self, user_id: str | None = None) -> None:
        if user_id is None:
            self._profiles.clear()
        else:
            self._profiles.pop(user_id, None)
