"""Permissions — role-based access to knowledge graph features.

Follows the suite-wide RBAC vocabulary (admin, analyst, viewer) with
per-operation allowlists. Keep permissions in sync with the RBAC layer of
the platform when exposed through the API.
"""
from __future__ import annotations

from typing import Any

_ROLE_RANKS = {"viewer": 1, "analyst": 2, "admin": 3}

# operation -> minimum role
_OPERATION_ROLE: dict[str, str] = {
    # Read-only operations: any authenticated user.
    "graph.read": "viewer",
    "search": "viewer",
    "query": "viewer",
    "reports.read": "viewer",
    # Analysis / build operations.
    "scan": "analyst",
    "build": "analyst",
    "reindex": "analyst",
    "analyze": "analyst",
    "export": "analyst",
    # Administrative operations.
    "configure": "admin",
    "manage_plugins": "admin",
    "manage_agents": "admin",
    "manage_schedules": "admin",
    "delete": "admin",
    "reset": "admin",
    "manage_users": "admin",
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
