from __future__ import annotations

from typing import Callable, Any


class Authorizer:
    """Composition root combining RBAC, ABAC, and policy engines."""

    def __init__(self) -> None:
        from .abac import ABACEngine
        from .rbac import RBACEngine

        self.rbac = RBACEngine()
        self.abac = ABACEngine()
        self._policies: list[Any] = []

    def authorize(self, user: dict, action: str, resource: str) -> bool:
        role = user.get("role", "") if isinstance(user, dict) else ""
        if role and self.rbac.has_role(role):
            return self.rbac.has_permission(role, action)
        if isinstance(user, dict):
            return self.abac.evaluate(action, user, {}, {})
        return False

    def to_dict(self) -> dict:
        return {"rbac": self.rbac.to_dict(), "abac": self.abac.to_dict()}
