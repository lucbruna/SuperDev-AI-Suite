"""
Security Context
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SecurityContext:
    user_id: str | None = None
    organization_id: str | None = None
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    ip_address: str = ""
    user_agent: str = ""
    session_id: str | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles

    def has_role(self, role: str) -> bool:
        return role in self.roles or "admin" in self.roles

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or "admin" in self.permissions

    def has_any_permission(self, permissions: list[str]) -> bool:
        return any(self.has_permission(p) for p in permissions)

    def has_all_permissions(self, permissions: list[str]) -> bool:
        return all(self.has_permission(p) for p in permissions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "roles": self.roles,
            "permissions": self.permissions,
            "ip_address": self.ip_address,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SecurityContext":
        return cls(
            user_id=data.get("user_id"),
            organization_id=data.get("organization_id"),
            roles=data.get("roles", []),
            permissions=data.get("permissions", []),
            ip_address=data.get("ip_address", ""),
            session_id=data.get("session_id"),
        )
