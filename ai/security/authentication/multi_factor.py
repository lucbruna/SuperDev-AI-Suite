"""Multi-factor authentication."""

from __future__ import annotations

import secrets
from typing import Any


class MultiFactorAuth:
    def __init__(self) -> None:
        self._mfa_codes: dict[str, str] = {}
        self._enabled_users: set[str] = set()

    def enable(self, user_id: str) -> dict[str, Any]:
        self._enabled_users.add(user_id)
        return {"user_id": user_id, "mfa_enabled": True}

    def generate_code(self, user_id: str) -> str:
        code = str(secrets.randbelow(900000) + 100000)
        self._mfa_codes[user_id] = code
        return code

    def verify_code(self, user_id: str, code: str) -> dict[str, Any]:
        if user_id not in self._enabled_users:
            return {"verified": False, "error": "mfa_not_enabled"}
        expected = self._mfa_codes.get(user_id)
        if expected and expected == code:
            del self._mfa_codes[user_id]
            return {"verified": True}
        return {"verified": False, "error": "invalid_code"}

    def is_enabled(self, user_id: str) -> bool:
        return user_id in self._enabled_users
