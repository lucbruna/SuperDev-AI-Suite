from __future__ import annotations

from typing import Any


class PlannerSecurity:
    """Security checks for planner operations."""

    ALLOWED_ACTIONS: set[str] = {
        "plan.create", "plan.read", "plan.update", "plan.delete",
        "plan.execute", "task.create", "task.read", "task.update",
    }

    def __init__(self):
        self._permissions: dict[str, set[str]] = {}

    def check_access(self, user_id: str, action: str) -> bool:
        if action not in self.ALLOWED_ACTIONS:
            return False
        user_perms = self._permissions.get(user_id, set())
        if "plan.*" in user_perms:
            return True
        return action in user_perms

    def grant(self, user_id: str, action: str) -> None:
        if user_id not in self._permissions:
            self._permissions[user_id] = set()
        self._permissions[user_id].add(action)

    def revoke(self, user_id: str, action: str) -> None:
        if user_id in self._permissions:
            self._permissions[user_id].discard(action)

    def health(self) -> dict[str, Any]:
        return {"status": "healthy", "users": len(self._permissions)}
