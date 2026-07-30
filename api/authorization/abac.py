from __future__ import annotations

from typing import Any, Callable


class ABACEngine:
    """Attribute-Based Access Control engine."""

    def __init__(self) -> None:
        self._policies: dict[str, Callable] = {}

    def register_policy(self, name: str, policy_fn: Callable) -> None:
        self._policies[name] = policy_fn

    def evaluate(
        self,
        user_attrs: dict[str, Any],
        resource_attrs: dict[str, Any],
        action: str,
        context: dict[str, Any] | None = None,
    ) -> bool:
        context = context or {}
        for policy_name, policy_fn in self._policies.items():
            try:
                result = policy_fn(user_attrs, resource_attrs, action, context)
                if hasattr(result, "__await__"):
                    import asyncio
                    result = asyncio.ensure_future(result)
                if result is False:
                    return False
            except Exception:
                continue
        return True

    def list_policies(self) -> list[str]:
        return list(self._policies.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "policies": self.list_policies(),
            "count": len(self._policies),
        }


def resource_owner_policy(
    user_attrs: dict[str, Any],
    resource_attrs: dict[str, Any],
    action: str,
    context: dict[str, Any],
) -> bool:
    """Allow access if user is the resource owner."""
    user_id = user_attrs.get("id", "")
    owner_id = resource_attrs.get("owner_id", "")
    return user_id == owner_id


def department_policy(
    user_attrs: dict[str, Any],
    resource_attrs: dict[str, Any],
    action: str,
    context: dict[str, Any],
) -> bool:
    """Allow access if user and resource are in the same department."""
    user_dept = user_attrs.get("department", "")
    resource_dept = resource_attrs.get("department", "")
    return user_dept and user_dept == resource_dept
