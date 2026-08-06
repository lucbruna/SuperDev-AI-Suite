"""Permission model for the Self-Healing Engine module.

Roles are hierarchical: viewer < operator < admin. Each role grants a fixed
set of permissions; ``can()`` is the single check used by the CLI, API and
engines.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.self_healing_engine.config.constants import (
    PERM_APPROVE_REPAIRS,
    PERM_EXECUTE_REPAIRS,
    PERM_MANAGE_ENGINE,
    PERM_RUN_DIAGNOSTICS,
    PERM_VIEW_HEALTH,
    ROLE_ADMIN,
    ROLE_OPERATOR,
    ROLE_VIEWER,
    ROLES,
)

_ROLE_GRANTS: dict[str, frozenset[str]] = {
    ROLE_VIEWER: frozenset({PERM_VIEW_HEALTH}),
    ROLE_OPERATOR: frozenset({
        PERM_VIEW_HEALTH,
        PERM_RUN_DIAGNOSTICS,
        PERM_EXECUTE_REPAIRS,
    }),
    ROLE_ADMIN: frozenset({
        PERM_VIEW_HEALTH,
        PERM_RUN_DIAGNOSTICS,
        PERM_APPROVE_REPAIRS,
        PERM_EXECUTE_REPAIRS,
        PERM_MANAGE_ENGINE,
    }),
}


@dataclass(slots=True)
class Permissions:
    """Resolved permission set for a caller role."""

    role: str = ROLE_VIEWER
    grants: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        # Always grant at least what the role implies; explicit grants are
        # additive on top of the role matrix.
        base = _ROLE_GRANTS.get(self.role, _ROLE_GRANTS[ROLE_VIEWER])
        self.grants = frozenset(set(base) | set(self.grants))

    def can(self, permission: str) -> bool:
        return permission in self.grants

    @classmethod
    def for_role(cls, role: str) -> "Permissions":
        if role not in ROLES:
            role = ROLE_VIEWER
        return cls(role=role)

    def to_dict(self) -> dict[str, object]:
        return {"role": self.role, "grants": sorted(self.grants)}
