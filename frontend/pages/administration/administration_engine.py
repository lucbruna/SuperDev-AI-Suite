from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class AdministrationEngine:
    """Renders the administration page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.administration")
        self._context = context or FrontendContext()
        self._users: dict[str, dict[str, Any]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "administration",
            "users": self.list_users(),
            "count": len(self._users),
        }

    def list_users(self) -> list[dict[str, Any]]:
        return [
            {"user_id": user_id, **user}
            for user_id, user in self._users.items()
        ]

    def add_user(self, email: str, role: str = "member") -> str:
        user_id = f"user-{len(self._users) + 1}"
        self._users[user_id] = {"email": email, "role": role, "created_at": time.time()}
        return user_id

    def remove_user(self, user_id: str) -> bool:
        return self._users.pop(user_id, None) is not None

    def set_role(self, user_id: str, role: str) -> bool:
        user = self._users.get(user_id)
        if user is None:
            return False
        user["role"] = role
        return True
