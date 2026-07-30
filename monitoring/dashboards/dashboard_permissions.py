from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DashboardRole(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"


@dataclass
class DashboardPermission:
    dashboard_id: str = ""
    user: str = ""
    role: DashboardRole = DashboardRole.VIEWER
    granted_at: float = field(default_factory=time.time)
    granted_by: str = ""


class DashboardPermissions:
    """Manages user permissions for dashboards."""

    def __init__(self) -> None:
        self._permissions: list[DashboardPermission] = []

    def grant(self, dashboard_id: str, user: str, role: DashboardRole, granted_by: str = "") -> None:
        self.revoke(dashboard_id, user)
        perm = DashboardPermission(
            dashboard_id=dashboard_id,
            user=user,
            role=role,
            granted_by=granted_by,
        )
        self._permissions.append(perm)

    def revoke(self, dashboard_id: str, user: str) -> bool:
        before = len(self._permissions)
        self._permissions = [
            p for p in self._permissions
            if not (p.dashboard_id == dashboard_id and p.user == user)
        ]
        return len(self._permissions) < before

    def check(self, dashboard_id: str, user: str, required_role: DashboardRole) -> bool:
        role_order = [DashboardRole.VIEWER, DashboardRole.EDITOR, DashboardRole.ADMIN, DashboardRole.OWNER]
        required_idx = role_order.index(required_role)

        for perm in self._permissions:
            if perm.dashboard_id == dashboard_id and perm.user == user:
                user_idx = role_order.index(perm.role)
                return user_idx >= required_idx
        return False

    def can_view(self, dashboard_id: str, user: str) -> bool:
        return self.check(dashboard_id, user, DashboardRole.VIEWER)

    def can_edit(self, dashboard_id: str, user: str) -> bool:
        return self.check(dashboard_id, user, DashboardRole.EDITOR)

    def can_admin(self, dashboard_id: str, user: str) -> bool:
        return self.check(dashboard_id, user, DashboardRole.ADMIN)

    def get_permissions(self, dashboard_id: str) -> list[DashboardPermission]:
        return [p for p in self._permissions if p.dashboard_id == dashboard_id]

    def get_user_permissions(self, user: str) -> list[DashboardPermission]:
        return [p for p in self._permissions if p.user == user]
