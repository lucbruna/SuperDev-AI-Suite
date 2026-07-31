"""User engine."""
from __future__ import annotations

import time
from typing import Any


class UserEngine:
    def __init__(self) -> None:
        self._users: dict[str, dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def create(self, email: str, name: str, org_id: str = "", role: str = "member") -> dict[str, Any]:
        import uuid
        user_id = str(uuid.uuid4())[:8]
        user = {"id": user_id, "email": email, "name": name, "org_id": org_id, "role": role, "status": "active", "created_at": time.time()}
        self._users[user_id] = user
        return user
    def get(self, user_id: str) -> dict[str, Any] | None:
        return self._users.get(user_id)
    def get_by_email(self, email: str) -> dict[str, Any] | None:
        for u in self._users.values():
            if u.get("email") == email:
                return u
        return None
    def update(self, user_id: str, **kwargs: Any) -> dict[str, Any] | None:
        user = self._users.get(user_id)
        if user:
            user.update(kwargs)
            return user
        return None
    def delete(self, user_id: str) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._users.values())
    def list_by_org(self, org_id: str) -> list[dict[str, Any]]:
        return [u for u in self._users.values() if u.get("org_id") == org_id]
    def count(self) -> int:
        return len(self._users)
