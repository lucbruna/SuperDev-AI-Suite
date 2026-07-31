"""Security for the Finance Intelligence Engine (Volume 35).

Approval roles, amount-based gating and sanitization so financial
operations only happen within granted authority.
"""

from __future__ import annotations

import re
from typing import Any

from finance_intelligence.finance_models import RiskLevel


class FinanceSecurity:
    """Permission checks, approval policy and sanitization."""

    def __init__(self, approval_threshold: float = 50000.0) -> None:
        self._approval_threshold = float(approval_threshold)
        self._approval_roles: set[str] = {"admin", "finance",
                                          "manager", "director"}
        self._permission_overrides: dict[str, list[str]] = {}

    # -- permissions ---------------------------------------------------------
    def grant(self, actor: str, permission: str) -> None:
        self._permission_overrides.setdefault(actor, []).append(permission)

    def can(self, actor: str, permission: str,
            granted: list[str] | None = None) -> bool:
        explicit = self._permission_overrides.get(actor, [])
        combined = list(explicit) + list(granted or [])
        return "*" in combined or permission in combined

    # -- approval policy -----------------------------------------------------
    def approve(self, actor: str) -> bool:
        return actor.lower() in self._approval_roles

    def requires_approval(self, amount: float,
                          risk_level: RiskLevel = RiskLevel.LOW) -> bool:
        return amount > self._approval_threshold or risk_level in (
            RiskLevel.HIGH, RiskLevel.CRITICAL)

    # -- sanitization --------------------------------------------------------
    _BLOCKED = re.compile(r"<\s*(script|iframe|object|embed)", re.IGNORECASE)

    def sanitize(self, text: str) -> str:
        cleaned = re.sub(r"<\s*(script|style)[^>]*>.*?</\s*(script|style)>",
                         "", text or "", flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        return re.sub(r"\s+", " ", cleaned).strip()

    def is_safe(self, text: str) -> bool:
        return not self._BLOCKED.search(text or "")

    # -- audit hook ----------------------------------------------------------
    def audit_deny(self, actor: str, target: str) -> None:
        """Overridable hook; the manager may record the denial."""
