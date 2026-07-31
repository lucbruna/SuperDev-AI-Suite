"""Internal access control for the Security Engine itself (Volume 16).

Guards who can run destructive security operations (vault access, key
rotation, policy changes) and keeps an audit trail of those decisions.
"""

from __future__ import annotations

import time
from typing import Any


class SecurityGuard:
    """Role-based guard for sensitive security operations."""

    # Operations that require elevated privileges.
    ELEVATED_OPERATIONS = {
        "vault.read",
        "vault.write",
        "vault.delete",
        "key.rotate",
        "policy.change",
        "certificate.issue",
        "threat.mitigate",
    }

    def __init__(self, admin_roles: tuple[str, ...] = ("admin", "security-admin")) -> None:
        self._admin_roles = set(admin_roles)
        self._audit: list[dict[str, Any]] = []
        self._audit_limit = 500

    def can_access(self, operation: str, roles: list[str] | set[str] | None) -> bool:
        """Check whether the given roles may perform the operation."""
        if operation not in self.ELEVATED_OPERATIONS:
            return True
        role_set = set(roles or [])
        return bool(role_set & self._admin_roles)

    def audit(self, operation: str, actor: str, allowed: bool, reason: str = "") -> None:
        entry = {
            "ts": time.time(),
            "operation": operation,
            "actor": actor,
            "allowed": allowed,
            "reason": reason,
        }
        self._audit.append(entry)
        if len(self._audit) > self._audit_limit:
            self._audit = self._audit[-self._audit_limit:]

    def audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._audit[-limit:]

    def snapshot(self) -> dict[str, Any]:
        return {"audit_entries": len(self._audit), "admin_roles": sorted(self._admin_roles)}
