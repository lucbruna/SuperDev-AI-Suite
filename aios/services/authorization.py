"""AIOS Authorization Service — role-based access control.

Maps roles to permissions and evaluates permission checks with
optional resource scoping ("permission" or "permission:resource").
"""

from __future__ import annotations

from typing import Any

ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ROLE_AGENT = "agent"
ROLE_VIEWER = "viewer"


class AuthorizationService:
    """RBAC permission evaluation."""

    def __init__(self) -> None:
        self._role_permissions: dict[str, set[str]] = {
            ROLE_ADMIN: {"*"},
            ROLE_OPERATOR: {"read", "write", "execute", "publish"},
            ROLE_AGENT: {"read", "execute"},
            ROLE_VIEWER: {"read"},
        }

    def define_role(self, role: str, permissions: list[str]) -> "AuthorizationService":
        self._role_permissions[role] = set(permissions)
        return self

    def grant(self, role: str, *permissions: str) -> "AuthorizationService":
        self._role_permissions.setdefault(role, set()).update(permissions)
        return self

    def roles(self) -> list[str]:
        return sorted(self._role_permissions)

    def check(self, roles: list[str], permission: str, resource: str | None = None) -> bool:
        target = permission if resource is None else f"{permission}:{resource}"
        for role in roles:
            allowed = self._role_permissions.get(role, set())
            if "*" in allowed or permission in allowed or target in allowed:
                return True
        return False

    def require(self, roles: list[str], permission: str, resource: str | None = None) -> None:
        if not self.check(roles, permission, resource):
            raise PermissionError(
                f"roles={roles} lack permission={permission!r} on resource={resource!r}"
            )

    def snapshot(self) -> dict[str, Any]:
        return {role: sorted(perms) for role, perms in sorted(self._role_permissions.items())}
