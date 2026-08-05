"""Permission Bridge — role-based access checks (reuses the studio permission model)."""
from __future__ import annotations

from typing import Any

#: role -> allowed capabilities
_ROLE_MATRIX: dict[str, tuple[str, ...]] = {
    "viewer": ("view",),
    "editor": ("view", "edit", "render"),
    "operator": ("view", "edit", "render", "export"),
    "admin": ("view", "edit", "render", "export", "manage", "audit"),
}


class PermissionBridge:
    """Checks capability access per role."""

    def check(self, role: str, capability: str) -> dict[str, Any]:
        allowed = _ROLE_MATRIX.get(role, ())
        return {
            "role": role,
            "capability": capability,
            "granted": capability in allowed,
        }

    def roles(self) -> list[dict[str, Any]]:
        return [{"role": r, "capabilities": list(c)} for r, c in _ROLE_MATRIX.items()]


_permission_bridge: PermissionBridge | None = None


def get_permission_bridge() -> PermissionBridge:
    global _permission_bridge
    if _permission_bridge is None:
        _permission_bridge = PermissionBridge()
    return _permission_bridge
