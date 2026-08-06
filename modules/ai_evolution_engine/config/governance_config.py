"""Governance configuration: policies and approval rules."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class GovernanceConfig:
    """Deterministic governance behaviour."""

    require_approval: bool = True
    auto_approve_severity: str = "info"  # severities <= this are auto-approved
    max_approvals: int = 1
    audit_enabled: bool = True
    audit_keep_entries: int = 2000
    allowed_recommendation_kinds: tuple[str, ...] = (
        "architecture",
        "dependency",
        "performance",
        "security",
        "modernization",
        "workflow",
        "plugin",
        "database",
        "api",
    )
