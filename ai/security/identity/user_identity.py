"""User identity management."""
from __future__ import annotations

import time
from typing import Any


class UserIdentityManager:
    def __init__(self) -> None:
        self._users: dict[str, dict[str, Any]] = {}
    def create(self, user_id: str, username: str, email: str, role: str = "viewer") -> dict[str, Any]:
        user = {"user_id": user_id, "username": username, "email": email, "role": role, "active": True, "created_at": time.time()}
        self._users[user_id] = user
        return user
    def get(self, user_id: str) -> dict[str, Any] | None:
        return dict(self._users[user_id]) if user_id in self._users else None
    def deactivate(self, user_id: str) -> bool:
        if user_id in self._users:
            self._users[user_id]["active"] = False
            return True
        return False
    def count(self) -> int:
        return len(self._users)
