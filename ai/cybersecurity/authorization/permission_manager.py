"""
Permission Manager
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Permission:
    name: str
    resource: str = ""
    action: str = ""
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class PermissionManager:
    def __init__(self):
        self.permissions: dict[str, Permission] = {}
        self.user_permissions: dict[str, set[str]] = {}
        self.role_permissions: dict[str, set[str]] = {}

    def create_permission(self, name: str, resource: str = "", action: str = "", description: str = "") -> Permission:
        perm = Permission(name=name, resource=resource, action=action, description=description)
        self.permissions[name] = perm
        return perm

    def get_permission(self, name: str) -> Permission | None:
        return self.permissions.get(name)

    def list_permissions(self) -> list[Permission]:
        return list(self.permissions.values())

    def grant_to_user(self, user_id: str, permission_name: str) -> bool:
        if permission_name not in self.permissions:
            return False
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
        self.user_permissions[user_id].add(permission_name)
        return True

    def revoke_from_user(self, user_id: str, permission_name: str) -> bool:
        if user_id in self.user_permissions:
            self.user_permissions[user_id].discard(permission_name)
            return True
        return False

    def grant_to_role(self, role_name: str, permission_name: str) -> bool:
        if permission_name not in self.permissions:
            return False
        if role_name not in self.role_permissions:
            self.role_permissions[role_name] = set()
        self.role_permissions[role_name].add(permission_name)
        return True

    def revoke_from_role(self, role_name: str, permission_name: str) -> bool:
        if role_name in self.role_permissions:
            self.role_permissions[role_name].discard(permission_name)
            return True
        return False

    def has_permission(self, user_id: str, permission_name: str) -> bool:
        return permission_name in self.user_permissions.get(user_id, set())

    def get_user_permissions(self, user_id: str) -> set[str]:
        return self.user_permissions.get(user_id, set()).copy()

    def count(self) -> int:
        return len(self.permissions)
