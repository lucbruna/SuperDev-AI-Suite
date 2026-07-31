"""
Permission Check
"""
from dataclasses import dataclass, field


@dataclass
class PermissionCheck:
    user_permissions: set[str] = field(default_factory=set)

    def has(self, permission: str) -> bool:
        return permission in self.user_permissions or "admin" in self.user_permissions

    def has_any(self, permissions: list[str]) -> bool:
        return bool(set(permissions).intersection(self.user_permissions))

    def has_all(self, permissions: list[str]) -> bool:
        return set(permissions).issubset(self.user_permissions)

    def set_permissions(self, permissions: set[str]) -> None:
        self.user_permissions = permissions

    def add_permission(self, permission: str) -> None:
        self.user_permissions.add(permission)

    def remove_permission(self, permission: str) -> None:
        self.user_permissions.discard(permission)

    def render(self) -> dict:
        return {"permissions": list(self.user_permissions)}
