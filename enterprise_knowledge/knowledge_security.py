"""Security for the Knowledge Graph & Enterprise Memory Engine.

Sanitization, RBAC and access-level enforcement so that e.g. an HR
employee cannot read director salaries.
"""

from __future__ import annotations

import re
from typing import Any

from enterprise_knowledge.knowledge_models import AccessLevel
from enterprise_knowledge.knowledge_protocols import coerce_bool

_ROLE_LEVELS = {
    "guest": AccessLevel.PUBLIC,
    "employee": AccessLevel.INTERNAL,
    "manager": AccessLevel.CONFIDENTIAL,
    "admin": AccessLevel.RESTRICTED,
}

_LEVEL_RANK = {
    AccessLevel.PUBLIC: 0,
    AccessLevel.INTERNAL: 1,
    AccessLevel.CONFIDENTIAL: 2,
    AccessLevel.RESTRICTED: 3,
}

_BLOCKED_PATTERNS = [
    re.compile(r"<\s*(script|iframe|object|embed)", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
]


class EnterpriseKnowledgeSecurity:
    """Sanitization + RBAC + access-level gates."""

    def __init__(self) -> None:
        self._role_levels = dict(_ROLE_LEVELS)

    # -- sanitization -------------------------------------------------------
    def sanitize(self, text: str) -> str:
        cleaned = re.sub(r"<\s*(script|style)[^>]*>.*?</\s*(script|style)>",
                         "", text or "", flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        return re.sub(r"\s+", " ", cleaned).strip()

    def is_safe(self, text: str) -> bool:
        return not any(pattern.search(text or "")
                       for pattern in _BLOCKED_PATTERNS)

    # -- access levels ------------------------------------------------------
    def role_level(self, role: str) -> AccessLevel:
        return self._role_levels.get(role.lower(), AccessLevel.PUBLIC)

    def can_access(self, role: str, level: AccessLevel) -> bool:
        return _LEVEL_RANK[self.role_level(role)] >= _LEVEL_RANK[level]

    def require(self, role: str, level: AccessLevel) -> bool:
        allowed = self.can_access(role, level)
        if not allowed:
            self.audit_deny(role, f"access:{level.value}")
        return allowed

    # -- RBAC ---------------------------------------------------------------
    def can(self, role: str, permission: str) -> bool:
        """Coarse RBAC: admin/manager grant every permission."""
        role = role.lower()
        if role == "admin":
            return True
        if role == "manager" and not permission.startswith("system."):
            return True
        if role == "employee":
            return permission.startswith(("read.", "search.", "ask."))
        return permission == "read.public"

    # -- audit hook ---------------------------------------------------------
    def audit_deny(self, actor: str, target: str) -> None:
        """Overridable hook; governance engine may record the denial."""
