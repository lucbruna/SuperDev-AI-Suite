"""Avatar permissions — role-based access control for avatar operations."""
from __future__ import annotations


# action → minimum role
_ACTION_ROLES: dict[str, str] = {
    "view": "viewer",
    "generate": "editor",
    "train": "trainer",
    "export": "editor",
    "publish": "admin",
    "delete": "admin",
}

_ROLE_LEVEL = {"viewer": 1, "editor": 2, "trainer": 3, "admin": 4}


class AvatarPermissions:
    """Check whether a role may perform an action."""

    def check(self, role: str, action: str) -> bool:
        required = _ACTION_ROLES.get(action, "viewer")
        return _ROLE_LEVEL.get(role, 0) >= _ROLE_LEVEL.get(required, 1)

    def require(self, role: str, action: str) -> None:
        if not self.check(role, action):
            raise PermissionError(f"role '{role}' cannot perform '{action}'")

    def actions(self) -> list[str]:
        return sorted(_ACTION_ROLES)


_avatar_permissions: AvatarPermissions | None = None


def get_avatar_permissions() -> AvatarPermissions:
    global _avatar_permissions
    if _avatar_permissions is None:
        _avatar_permissions = AvatarPermissions()
    return _avatar_permissions
