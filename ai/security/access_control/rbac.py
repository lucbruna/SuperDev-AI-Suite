"""RBAC (Role-Based Access Control)."""

from __future__ import annotations


class RBACRole:
    def __init__(self, name: str, description: str = "", parent: str = "") -> None:
        self.name = name
        self.description = description
        self.parent = parent
        self.permissions: set[str] = set()
        self.active = True


class RBACManager:
    def __init__(self) -> None:
        self._roles: dict[str, RBACRole] = {}
        self._user_roles: dict[str, set[str]] = {}
        self._role_permissions: dict[str, set[str]] = {}

    def create_role(self, name: str, description: str = "", parent: str = "") -> RBACRole:
        role = RBACRole(name, description, parent)
        self._roles[name] = role
        return role

    def delete_role(self, name: str) -> bool:
        if name in self._roles:
            del self._roles[name]
            return True
        return False

    def assign_role(self, user_id: str, role: str) -> bool:
        if role in self._roles:
            self._user_roles.setdefault(user_id, set()).add(role)
            return True
        return False

    def revoke_role(self, user_id: str, role: str) -> bool:
        if user_id in self._user_roles:
            self._user_roles[user_id].discard(role)
            return True
        return False

    def grant_permission(self, role: str, permission: str) -> bool:
        if role in self._roles:
            self._role_permissions.setdefault(role, set()).add(permission)
            return True
        return False

    def revoke_permission(self, role: str, permission: str) -> bool:
        if role in self._role_permissions:
            self._role_permissions[role].discard(permission)
            return True
        return False

    def get_user_roles(self, user_id: str) -> list[str]:
        return sorted(self._user_roles.get(user_id, set()))

    def get_role_permissions(self, role: str) -> list[str]:
        return sorted(self._role_permissions.get(role, set()))

    def get_user_permissions(self, user_id: str) -> list[str]:
        roles = self._user_roles.get(user_id, set())
        perms: set[str] = set()
        for role in roles:
            perms |= self._role_permissions.get(role, set())
        return sorted(perms)

    def has_permission(self, user_id: str, permission: str) -> bool:
        return permission in self.get_user_permissions(user_id)

    def list_roles(self) -> list[str]:
        return sorted(self._roles.keys())

    def list_users(self) -> list[str]:
        return sorted(self._user_roles.keys())
