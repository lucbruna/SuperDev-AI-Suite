"""Authentication engine."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any


class AuthenticationEngine:
    def __init__(self) -> None:
        self._users: dict[str, dict[str, Any]] = {}
        self._tokens: dict[str, str] = {}
        self._failed_attempts: dict[str, int] = {}
        self._max_attempts = 5

    def register_user(self, username: str, password: str, email: str = "") -> dict[str, Any]:
        uid = str(uuid.uuid4())[:8]
        hashed = hashlib.sha256(password.encode()).hexdigest()
        self._users[username] = {"user_id": uid, "password_hash": hashed, "email": email, "active": True}
        return {"user_id": uid, "username": username, "status": "registered"}

    def authenticate(self, username: str, password: str) -> dict[str, Any]:
        user = self._users.get(username)
        if not user:
            return {"authenticated": False, "error": "user_not_found"}
        if self._failed_attempts.get(username, 0) >= self._max_attempts:
            return {"authenticated": False, "error": "account_locked"}
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if user["password_hash"] == hashed:
            token = str(uuid.uuid4())
            self._tokens[token] = username
            self._failed_attempts[username] = 0
            return {"authenticated": True, "token": token, "user_id": user["user_id"]}
        self._failed_attempts[username] = self._failed_attempts.get(username, 0) + 1
        return {"authenticated": False, "error": "invalid_password"}

    def validate_token(self, token: str) -> str | None:
        return self._tokens.get(token)

    def revoke_token(self, token: str) -> bool:
        if token in self._tokens:
            del self._tokens[token]
            return True
        return False

    def snapshot(self) -> dict[str, Any]:
        return {"users": len(self._users), "active_tokens": len(self._tokens)}
