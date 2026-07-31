from __future__ import annotations

import logging
import secrets
import time
from typing import Any

from .jwt import JWTProvider


class TokenManager:
    """Issues, validates, refreshes, and revokes access tokens."""

    def __init__(self, secret: str = "superdev-token-secret", ttl: int = 3600) -> None:
        self._log = logging.getLogger("superdev.integration.auth.tokens")
        self._jwt = JWTProvider(secret)
        self.ttl = ttl
        self._blacklist: set[str] = set()
        self._refresh_tokens: dict[str, str] = {}  # refresh_token -> subject

    def issue(self, subject: str, scopes: list[str] | None = None,
              ttl: int | None = None) -> str:
        return self._jwt.encode(
            {"sub": subject, "scopes": scopes or []}, ttl=ttl or self.ttl
        )

    def validate(self, token: str) -> dict[str, Any]:
        if token in self._blacklist:
            raise ValueError("token revoked")
        return self._jwt.decode(token)

    def subject(self, token: str) -> str | None:
        try:
            return self.validate(token).get("sub")
        except ValueError:
            return None

    def revoke(self, token: str) -> bool:
        try:
            self._jwt.decode(token)
        except ValueError:
            return False
        self._blacklist.add(token)
        return True

    def create_refresh_token(self, subject: str) -> str:
        refresh = secrets.token_hex(24)
        self._refresh_tokens[refresh] = subject
        return refresh

    def refresh(self, refresh_token: str) -> str | None:
        """Exchanges a refresh token for a new access token."""
        subject = self._refresh_tokens.get(refresh_token)
        if subject is None:
            return None
        self._refresh_tokens.pop(refresh_token, None)
        return self.issue(subject)

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        return self._refresh_tokens.pop(refresh_token, None) is not None
