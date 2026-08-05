"""AIOS Authentication Service — token issue/verify.

Issues bearer tokens bound to a principal and roles, with expiry.
Deterministic and self-contained (no crypto dependency beyond hashlib).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from typing import Any


class AuthenticationService:
    """Token issuance and verification (HMAC-signed)."""

    def __init__(self, secret: str | None = None, token_ttl: float = 3600.0) -> None:
        self._secret = secret or secrets.token_hex(16)
        self._ttl = token_ttl
        self._issued = 0

    def _sign(self, payload: str) -> str:
        return hmac.new(self._secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

    def issue_token(
        self,
        principal: str,
        roles: list[str] | None = None,
        ttl: float | None = None,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Issue a signed token for ``principal``."""
        expires = time.time() + (self._ttl if ttl is None else ttl)
        body = {
            "principal": principal,
            "roles": roles or [],
            "expires": expires,
            "extra": extra or {},
        }
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":"))
        signature = self._sign(encoded)
        self._issued += 1
        return f"{encoded}.{signature}"

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify a token; return claims or a failure dict."""
        if "." not in token:
            return {"ok": False, "error": "malformed token"}
        encoded, signature = token.rsplit(".", 1)
        if not hmac.compare_digest(self._sign(encoded), signature):
            return {"ok": False, "error": "invalid signature"}
        try:
            claims = json.loads(encoded)
        except json.JSONDecodeError:
            return {"ok": False, "error": "invalid payload"}
        if claims.get("expires", 0) < time.time():
            return {"ok": False, "error": "token expired"}
        return {"ok": True, "claims": claims}

    def snapshot(self) -> dict[str, Any]:
        return {"tokens_issued": self._issued, "token_ttl": self._ttl}
