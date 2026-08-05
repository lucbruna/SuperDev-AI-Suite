"""Permission model for Architecture Graph API actions.

Uses the platform auth payload (dict with ``roles``) delivered by
``backend.dependencies.get_current_user``. Every capability has a default
role requirement, overridable through the SUPERDEV_GRAPH_PERMISSIONS env var.
"""
from __future__ import annotations

import os
from typing import Any

# capability -> minimum role required
DEFAULT_PERMISSIONS: dict[str, str] = {
    "view": "user",      # read graphs, metrics, exports, search
    "build": "user",     # trigger scans / rebuilds
    "export": "user",    # download generated artifacts
    "admin": "admin",    # storage backend changes, permission overrides
}

ROLE_RANK: dict[str, int] = {"user": 10, "developer": 20, "admin": 50}


def _overrides() -> dict[str, str]:
    """Parse SUPERDEV_GRAPH_PERMISSIONS="view=admin,build=developer"."""
    raw = os.getenv("SUPERDEV_GRAPH_PERMISSIONS", "")
    parsed: dict[str, str] = {}
    for part in raw.split(","):
        part = part.strip()
        if "=" in part:
            cap, role = part.split("=", 1)
            parsed[cap.strip()] = role.strip()
    return parsed


def required_role(capability: str) -> str:
    return _overrides().get(capability, DEFAULT_PERMISSIONS.get(capability, "admin"))


def can(user: dict[str, Any] | None, capability: str) -> bool:
    """Return True when the (possibly anonymous) user may perform the action."""
    if user is None:
        return False
    raw_roles: Any = user.get("roles") or []
    # Platform admins (is_superuser via payload) always pass.
    payload = user.get("payload") or {}
    if payload.get("superuser") or payload.get("is_superuser"):
        return True
    needed = required_role(capability)
    # Roles may be a list of role names or a single role string.
    role_list = [raw_roles] if isinstance(raw_roles, str) else list(raw_roles)
    effective = max((ROLE_RANK.get(r, 0) for r in role_list), default=0)
    return effective >= ROLE_RANK.get(needed, 50)
