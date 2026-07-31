"""User activity."""
from __future__ import annotations

import time
from typing import Any


class UserActivity:
    def __init__(self) -> None:
        self._activities: dict[str, list[dict[str, Any]]] = {}
    def log(self, user_id: str, action: str, resource: str = "", details: str = "") -> dict[str, Any]:
        entry = {"action": action, "resource": resource, "details": details, "timestamp": time.time()}
        self._activities.setdefault(user_id, []).append(entry)
        return entry
    def get_activities(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return self._activities.get(user_id, [])[-limit:]
    def get_last_activity(self, user_id: str) -> dict[str, Any]:
        activities = self._activities.get(user_id, [])
        return activities[-1] if activities else {}
    def count(self, user_id: str) -> int:
        return len(self._activities.get(user_id, []))
    def clear(self, user_id: str) -> int:
        n = len(self._activities.get(user_id, []))
        self._activities.pop(user_id, None)
        return n
    def get_active_users(self, hours: int = 24) -> list[str]:
        cutoff = time.time() - hours * 3600
        active = []
        for user_id, activities in self._activities.items():
            if activities and activities[-1]["timestamp"] > cutoff:
                active.append(user_id)
        return active
