from __future__ import annotations

from typing import Any


class RBACEngine:
    """Role-Based Access Control engine with role hierarchy."""

    def __init__(self) -> None:
        self._roles: dict[str, dict[str, Any]] = {}
        self._user_roles: dict[str, list[str]] = {}
        self._initialize_builtin_roles()

    def _initialize_builtin_roles(self) -> None:
        self.create_role("admin", "Full system access")
        self.create_role("manager", "Management access", parent="admin")
        self.create_role("editor", "Content editing access", parent="manager")
        self.create_role("viewer", "Read-only access", parent="editor")

        self.assign_permission_to_role("admin", "*")
        self.assign_permission_to_role("manager", "read:*")
        self.assign_permission_to_role("manager", "write:*")
        self.assign_permission_to_role("editor", "read:*")
        self.assign_permission_to_role("editor", "write:content")
        self.assign_permission_to_role("viewer", "read:*")

    def create_role(self, name: str, description: str = "", parent: str | None = None) -> None:
        self._roles[name] = {
            "name": name,
            "description": description,
            "parent": parent,
            "permissions": [],
        }

    def assign_permission_to_role(self, role_name: str, permission: str) -> bool:
        role = self._roles.get(role_name)
        if role is None:
            return False
        if permission not in role["permissions"]:
            role["permissions"].append(permission)
        return True

    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        if role_name not in self._roles:
            return False
        if user_id not in self._user_roles:
            self._user_roles[user_id] = []
        if role_name not in self._user_roles[user_id]:
            self._user_roles[user_id].append(role_name)
        return True

    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        roles = self._user_roles.get(user_id)
        if roles and role_name in roles:
            roles.remove(role_name)
            return True
        return False

    def get_user_roles(self, user_id: str) -> list[str]:
        return list(self._user_roles.get(user_id, []))

    def get_role_permissions(self, role_name: str) -> set[str]:
        role = self._roles.get(role_name)
        if role is None:
            return set()
        permissions = set(role["permissions"])
        parent = role.get("parent")
        if parent:
            permissions.update(self.get_role_permissions(parent))
        return permissions

    def get_user_permissions(self, user_id: str) -> set[str]:
        permissions: set[str] = set()
        for role_name in self.get_user_roles(user_id):
            permissions.update(self.get_role_permissions(role_name))
        return permissions

    def check_permission(self, user_id: str, permission: str) -> bool:
        user_permissions = self.get_user_permissions(user_id)
        if "*" in user_permissions:
            return True
        if permission in user_permissions:
            return True
        for up in user_permissions:
            if up.endswith(":*") and permission.startswith(up[:-1]):
                return True
        return False

    def list_roles(self) -> list[dict[str, Any]]:
        return [
            {"name": r["name"], "description": r["description"], "parent": r["parent"]}
            for r in self._roles.values()
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "roles": len(self._roles),
            "users_with_roles": len(self._user_roles),
            "role_list": self.list_roles(),
        }
