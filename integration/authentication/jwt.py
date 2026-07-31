from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import time
from typing import Any


class JWTProvider:
    """Minimal JWT implementation (HS256) for integration authentication."""

    def __init__(self, secret: str = "superdev-default-secret") -> None:
        self._log = logging.getLogger("superdev.integration.auth.jwt")
        self._secret = secret

    def encode(self, payload: dict[str, Any], ttl: int = 3600) -> str:
        claims = dict(payload)
        claims.setdefault("iat", int(time.time()))
        claims.setdefault("exp", int(time.time()) + ttl)
        header = {"alg": "HS256", "typ": "JWT"}
        segments = [
            self._b64url(json.dumps(header, separators=(",", ":")).encode()),
            self._b64url(json.dumps(claims, separators=(",", ":")).encode()),
        ]
        signing_input = ".".join(segments)
        signature = self._sign(signing_input)
        return f"{signing_input}.{signature}"

    def decode(self, token: str, verify: bool = True) -> dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("malformed token")
        header, payload, signature = parts
        if verify and self._sign(f"{header}.{payload}") != signature:
            raise ValueError("invalid signature")
        claims = json.loads(self._unb64url(payload))
        if verify:
            exp = claims.get("exp", 0)
            if exp and exp < int(time.time()):
                raise ValueError("token expired")
        return claims

    def validate(self, token: str) -> bool:
        try:
            self.decode(token)
            return True
        except (ValueError, TypeError):
            return False

    def _sign(self, message: str) -> str:
        digest = hmac.new(self._secret.encode(), message.encode(), hashlib.sha256).digest()
        return self._b64url(digest)

    @staticmethod
    def _b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    @staticmethod
    def _unb64url(data: str) -> bytes:
        padding = "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + padding)
