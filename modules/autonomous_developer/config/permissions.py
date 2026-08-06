"""Permissions — role-based access to Autonomous Developer features.

Roles follow the suite-wide RBAC vocabulary. The autonomous developer adds a
``developer`` role between read-only roles and administration; only admins can
merge, push or write to a main branch.
"""
from __future__ import annotations

from typing import Any

_ROLE_RANKS = {"viewer": 1, "developer": 2, "admin": 3}

# operation -> minimum role
_OPERATION_ROLE: dict[str, str] = {
    # Read-only operations: any authenticated user.
    "task.read": "viewer",
    "plan.read": "viewer",
    "reports.read": "viewer",
    "sessions.read": "viewer",
    # Development operations.
    "task.create": "developer",
    "task.execute": "developer",
    "generate_code": "developer",
    "modify_code": "developer",
    "refactor": "developer",
    "bugfix": "developer",
    "run_tests": "developer",
    "review": "developer",
    "write_docs": "developer",
    # Administrative operations.
    "merge": "admin",
    "push": "admin",
    "main_branch_write": "admin",
    "manage_agents": "admin",
    "manage_schedules": "admin",
    "configure": "admin",
    "manage_users": "admin",
    "delete": "admin",
}


def require_role(role: str, operation: str) -> bool:
    """Return True if ``role`` may perform ``operation``."""
    required = _OPERATION_ROLE.get(operation, "admin")
    return _ROLE_RANKS.get(role, 0) >= _ROLE_RANKS.get(required, 3)


def allowed_operations(role: str) -> list[str]:
    """Return every operation allowed for the given role."""
    rank = _ROLE_RANKS.get(role, 0)
    return [
        op for op, required in _OPERATION_ROLE.items()
        if rank >= _ROLE_RANKS.get(required, 3)
    ]


def check_permission(role: str | None, operation: str) -> dict[str, Any]:
    """Permission check returning a structured decision (for API responses)."""
    role = role or "viewer"
    allowed = require_role(role, operation)
    return {
        "allowed": allowed,
        "operation": operation,
        "role": role,
        "required_role": _OPERATION_ROLE.get(operation, "admin"),
    }
