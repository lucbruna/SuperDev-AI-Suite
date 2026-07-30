from __future__ import annotations

from typing import Any

from .tool_interfaces import ITool


class ToolPermissions:
    """Manages and checks tool permissions."""

    def __init__(self) -> None:
        self._user_permissions: dict[str, list[str]] = {}
        self._tool_overrides: dict[str, list[str]] = {}

    def set_user_permissions(self, user_id: str, permissions: list[str]) -> None:
        self._user_permissions[user_id] = permissions

    def get_user_permissions(self, user_id: str) -> list[str]:
        return self._user_permissions.get(user_id, [])

    def has_permission(self, user_id: str, permission: str) -> bool:
        perms = self._user_permissions.get(user_id, [])
        return permission in perms

    def check_tool_access(self, tool: ITool, user_id: str) -> bool:
        required = tool.permissions()
        user_perms = self._user_permissions.get(user_id, [])
        return all(p in user_perms for p in required)

    def set_tool_override(self, tool_name: str, permissions: list[str]) -> None:
        self._tool_overrides[tool_name] = permissions

    def get_effective_permissions(self, tool: ITool, user_id: str) -> list[str]:
        required = tool.permissions()
        user_perms = self._user_permissions.get(user_id, [])
        override = self._tool_overrides.get(tool.name())
        if override is not None:
            required = override
        return [p for p in required if p in user_perms]

    def to_dict(self) -> dict[str, Any]:
        return {
            "users": {k: list(v) for k, v in self._user_permissions.items()},
            "overrides": {k: list(v) for k, v in self._tool_overrides.items()},
        }
