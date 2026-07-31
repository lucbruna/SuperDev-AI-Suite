from __future__ import annotations

import html
import logging
from typing import Any


class KnowledgeSecurity:
    """Enforces access control and sanitization on knowledge content."""

    def __init__(self, enable_governance: bool = True) -> None:
        self._log = logging.getLogger("superdev.knowledge.security")
        self._enable_governance = enable_governance
        self._acl: dict[str, set[str]] = {}  # item_id -> allowed roles
        self._roles: dict[str, set[str]] = {"admin": {"*"}}

    def sanitize(self, value: str) -> str:
        return html.escape(value, quote=True)

    def sanitize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {str(k): html.escape(str(v), quote=True) for k, v in metadata.items()}

    def grant(self, user: str, role: str) -> None:
        self._roles.setdefault(user, set()).add(role)

    def check_permission(self, user: str, permission: str) -> bool:
        if not self._enable_governance:
            return True
        roles = self._roles.get(user, set())
        return "*" in roles or permission in roles

    def restrict(self, item_id: str, roles: list[str]) -> None:
        self._acl[item_id] = set(roles)

    def can_access(self, user: str, item_id: str) -> bool:
        if not self._enable_governance:
            return True
        user_roles = self._roles.get(user, set())
        if "*" in user_roles:
            return True
        required = self._acl.get(item_id, set())
        return bool(required & user_roles) if required else True

    def enforce(self, user: str, permission: str) -> None:
        if not self.check_permission(user, permission):
            raise PermissionError(f"user {user!r} lacks permission {permission!r}")
