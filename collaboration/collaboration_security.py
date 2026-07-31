"""Security helpers for the Collaboration & Team Workspace Engine."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import MemberRole


class CollaborationSecurity:
    """Sanitization, permissions and audit for collaboration operations."""

    def __init__(self) -> None:
        self._permissions: dict[str, set[str]] = {}
        self._audit: list[dict[str, Any]] = []

    # -- permissions --------------------------------------------------------
    def grant(self, role: str, resource: str) -> None:
        self._permissions.setdefault(role, set()).add(resource)

    def can(self, role: str, resource: str) -> bool:
        allowed = self._permissions.get(role, set())
        return "*" in allowed or resource in allowed

    # -- role helpers -------------------------------------------------------
    @staticmethod
    def role_value(role: MemberRole) -> int:
        order = {MemberRole.OWNER: 5, MemberRole.ADMIN: 4,
                 MemberRole.DEVELOPER: 3, MemberRole.REVIEWER: 3,
                 MemberRole.SECURITY: 3, MemberRole.ANALYST: 2,
                 MemberRole.VIEWER: 1}
        return order.get(role, 1)

    def at_least(self, member_role: MemberRole, required: MemberRole) -> bool:
        return self.role_value(member_role) >= self.role_value(required)

    # -- sanitization -------------------------------------------------------
    def sanitize(self, text: str, max_length: int = 2000) -> str:
        cleaned = " ".join(str(text or "").split())
        return cleaned[:max_length]

    # -- audit --------------------------------------------------------------
    def audit(self, member_id: str, action: str, resource: str) -> None:
        self._audit.append({"member_id": member_id, "action": action,
                            "resource": resource})

    def audit_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._audit[-limit:])
