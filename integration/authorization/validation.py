from __future__ import annotations

import logging
from typing import Any

from .access_policy import AccessPolicy
from .role_mapping import RoleMapper
from .scope_manager import ScopeManager


class PermissionValidator:
    """Validates authorization requests against role permissions and scopes."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.authorization.validation")
        self.roles = RoleMapper()
        self.scopes = ScopeManager()

    def check_permission(self, user: str, permission: str) -> bool:
        return self.roles.has_permission(user, permission)

    def enforce_permission(self, user: str, permission: str) -> None:
        if not self.check_permission(user, permission):
            raise PermissionError(f"user {user!r} lacks permission {permission!r}")

    def validate(self, user: str, permission: str,
                 granted_scopes: list[str] | None = None) -> bool:
        """Checks both role permission and scope membership when scopes given."""
        if not self.check_permission(user, permission):
            return False
        if granted_scopes:
            return self.scopes.check_any(granted_scopes, [permission])
        return True

    def snapshot(self) -> dict[str, int]:
        return {
            "users": self.roles.snapshot()["users"],
            "roles": self.roles.snapshot()["roles"],
            "scopes": self.scopes.snapshot()["scopes"],
        }
