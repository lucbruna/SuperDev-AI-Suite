from __future__ import annotations

import logging
from typing import Any


class PermissionsEngine:
    """RBAC permission checks for frontend actions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.permissions")
        self._roles: dict[str, list[str]] = {
            "admin": ["*"],
            "member": ["read", "create", "update"],
            "viewer": ["read"],
        }
        self._user_roles: dict[str, list[str]] = {}
        self._deny: set[str] = set()

    def assign_role(self, user: str, role: str) -> None:
        if role not in self._roles:
            raise KeyError(f"unknown role: {role}")
        self._user_roles.setdefault(user, [])
        if role not in self._user_roles[user]:
            self._user_roles[user].append(role)

    def revoke_role(self, user: str, role: str) -> bool:
        roles = self._user_roles.get(user, [])
        if role in roles:
            roles.remove(role)
            return True
        return False

    def define_role(self, role: str, permissions: list[str]) -> None:
        self._roles[role] = list(permissions)

    def roles_for(self, user: str) -> list[str]:
        return list(self._user_roles.get(user, []))

    def can(self, user: str, permission: str) -> bool:
        if permission in self._deny:
            return False
        for role in self._user_roles.get(user, []):
            permissions = self._roles.get(role, [])
            if "*" in permissions or permission in permissions:
                return True
        return False

    def require(self, user: str, permission: str) -> None:
        if not self.can(user, permission):
            raise PermissionError(f"user '{user}' lacks permission: {permission}")

    def deny(self, permission: str) -> None:
        self._deny.add(permission)

    def allow(self, permission: str) -> None:
        self._deny.discard(permission)

    def list_permissions(self, user: str) -> list[str]:
        granted = set()
        for role in self._user_roles.get(user, []):
            permissions = self._roles.get(role, [])
            if "*" in permissions:
                return ["*"]
            granted.update(permissions)
        return sorted(granted - self._deny)
