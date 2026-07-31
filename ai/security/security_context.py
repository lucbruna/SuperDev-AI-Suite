"""Security context for request-scoped security state."""

from __future__ import annotations

import time
from typing import Any


class SecurityContext:
    """Holds security state for the current request/operation."""

    def __init__(self) -> None:
        self._context: dict[str, Any] = {
            "user_id": "",
            "session_id": "",
            "ip_address": "",
            "user_agent": "",
            "roles": [],
            "permissions": [],
            "authenticated": False,
            "start_time": time.time(),
        }

    def set_user(self, user_id: str, roles: list[str] | None = None, permissions: list[str] | None = None) -> None:
        self._context["user_id"] = user_id
        self._context["roles"] = roles or []
        self._context["permissions"] = permissions or []
        self._context["authenticated"] = True

    def set_request(self, ip_address: str, user_agent: str = "", session_id: str = "") -> None:
        self._context["ip_address"] = ip_address
        self._context["user_agent"] = user_agent
        self._context["session_id"] = session_id

    def get(self, key: str, default: Any = None) -> Any:
        return self._context.get(key, default)

    def is_authenticated(self) -> bool:
        return self._context.get("authenticated", False)

    def has_role(self, role: str) -> bool:
        return role in self._context.get("roles", [])

    def has_permission(self, permission: str) -> bool:
        return permission in self._context.get("permissions", [])

    def get_user_id(self) -> str:
        return self._context.get("user_id", "")

    def to_dict(self) -> dict[str, Any]:
        return dict(self._context)

    def clear(self) -> None:
        self._context = {
            "user_id": "",
            "session_id": "",
            "ip_address": "",
            "user_agent": "",
            "roles": [],
            "permissions": [],
            "authenticated": False,
            "start_time": time.time(),
        }
