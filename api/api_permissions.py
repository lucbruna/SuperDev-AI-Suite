from __future__ import annotations

from typing import Any


class APIPermissions:
    """Granular permission management for API access control."""

    def __init__(self) -> None:
        self._role_permissions: dict[str, set[str]] = {}
        self._user_permissions: dict[str, set[str]] = {}

    def define_role(self, role: str, permissions: list[str]) -> None:
        self._role_permissions[role] = set(permissions)

    def assign_role(self, user_id: str, role: str) -> bool:
        if role not in self._role_permissions:
            return False
        self._user_permissions[user_id] = self._role_permissions[role].copy()
        return True

    def grant_user(self, user_id: str, permission: str) -> None:
        if user_id not in self._user_permissions:
            self._user_permissions[user_id] = set()
        self._user_permissions[user_id].add(permission)

    def revoke_user(self, user_id: str, permission: str) -> None:
        perms = self._user_permissions.get(user_id, set())
        perms.discard(permission)

    def has_permission(self, user_id: str, permission: str) -> bool:
        return permission in self._user_permissions.get(user_id, set())

    def has_any_permission(self, user_id: str, permissions: list[str]) -> bool:
        user_perms = self._user_permissions.get(user_id, set())
        return bool(user_perms & set(permissions))

    def get_user_permissions(self, user_id: str) -> set[str]:
        return self._user_permissions.get(user_id, set())

    def list_roles(self) -> list[str]:
        return list(self._role_permissions.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "roles": list(self._role_permissions.keys()),
            "users_with_permissions": len(self._user_permissions),
            "role_count": len(self._role_permissions),
        }
