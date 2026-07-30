from __future__ import annotations

from typing import Any


class PlannerPermissions:
    """Fine-grained permissions for planner resources."""

    def __init__(self):
        self._roles: dict[str, set[str]] = {
            "admin": {"planner.*", "plan.*", "task.*", "tool.*"},
            "user": {"plan.create", "plan.read", "plan.execute", "task.create", "task.read"},
            "viewer": {"plan.read", "task.read"},
        }

    def check(self, role: str, action: str) -> bool:
        role_perms = self._roles.get(role, set())
        for perm in role_perms:
            if perm.endswith(".*"):
                prefix = perm[:-2]
                if action.startswith(prefix):
                    return True
            elif perm == action:
                return True
        return False

    def health(self) -> dict[str, Any]:
        return {"status": "healthy", "roles": list(self._roles.keys())}
