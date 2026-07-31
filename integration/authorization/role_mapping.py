from __future__ import annotations

import logging
from typing import Any


class RoleMapper:
    """Maps users to roles and roles to permissions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.authorization.roles")
        self._user_roles: dict[str, set[str]] = {}
        self._role_permissions: dict[str, set[str]] = {}

    def define_role(self, role: str, permissions: list[str]) -> None:
        self._role_permissions[role] = set(permissions)

    def assign(self, user: str, role: str) -> None:
        self._user_roles.setdefault(user, set()).add(role)

    def unassign(self, user: str, role: str) -> bool:
        roles = self._user_roles.get(user)
        if roles is None or role not in roles:
            return False
        roles.discard(role)
        return True

    def roles_for(self, user: str) -> list[str]:
        return sorted(self._user_roles.get(user, set()))

    def permissions_for(self, user: str) -> set[str]:
        permissions: set[str] = set()
        for role in self._user_roles.get(user, set()):
            permissions |= self._role_permissions.get(role, set())
        return permissions

    def has_permission(self, user: str, permission: str) -> bool:
        permissions = self.permissions_for(user)
        if "*" in permissions:
            return True
        return permission in permissions

    def snapshot(self) -> dict[str, int]:
        return {"users": len(self._user_roles), "roles": len(self._role_permissions)}
