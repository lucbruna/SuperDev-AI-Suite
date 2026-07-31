from __future__ import annotations

import html
import logging
import secrets
import time
from typing import Any


class FrontendSecurity:
    """Enforces security policies on the frontend."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.security")
        self._tokens: dict[str, dict[str, Any]] = {}
        self._csrf: str | None = None
        self._roles: dict[str, list[str]] = {"admin": ["*"]}

    def issue_token(self, user: str, **kwargs: Any) -> str:
        token = secrets.token_hex(16)
        ttl = float(kwargs.get("ttl_seconds", 3600))
        self._tokens[token] = {"user": user, "expires_at": time.time() + ttl}
        return token

    def validate_token(self, token: str) -> dict[str, Any]:
        entry = self._tokens.get(token)
        if entry is None:
            raise ValueError("invalid token")
        if time.time() > entry["expires_at"]:
            self._tokens.pop(token, None)
            raise ValueError("expired token")
        return dict(entry)

    def revoke_token(self, token: str) -> bool:
        return self._tokens.pop(token, None) is not None

    def sanitize(self, value: str) -> str:
        return html.escape(value, quote=True)

    def check_permission(self, user: str, permission: str) -> bool:
        permissions = self._roles.get(user, [])
        return "*" in permissions or permission in permissions

    def grant_role(self, user: str, permissions: list[str]) -> None:
        self._roles.setdefault(user, [])
        self._roles[user].extend(p for p in permissions if p not in self._roles[user])
