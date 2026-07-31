"""Security for the Agent Orchestration Engine (Volume 31).

Agent identity, permission checks and risk gating hooks so that agents
only act within their granted scope.
"""

from __future__ import annotations

import re
from typing import Any

from agent_orchestration.orchestrator_models import RiskLevel


class OrchestratorSecurity:
    """Permission checks, sanitization and risk policy."""

    def __init__(self) -> None:
        self._permission_overrides: dict[str, list[str]] = {}
        self._approval_roles: set[str] = {"admin", "manager"}

    # -- permissions ---------------------------------------------------------
    def grant(self, agent_id: str, permission: str) -> None:
        self._permission_overrides.setdefault(agent_id, []).append(permission)

    def can(self, agent_id: str, permission: str,
            granted: list[str] | None = None) -> bool:
        explicit = self._permission_overrides.get(agent_id, [])
        combined = list(explicit) + list(granted or [])
        return "*" in combined or permission in combined

    # -- risk policy ---------------------------------------------------------
    def requires_approval(self, risk_level: RiskLevel,
                          require_high_risk: bool = True) -> bool:
        return require_high_risk and risk_level in (
            RiskLevel.HIGH, RiskLevel.CRITICAL)

    def approve(self, actor: str) -> bool:
        return actor.lower() in self._approval_roles

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
        """Overridable hook; manager may record the denial."""
