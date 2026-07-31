"""Token service for JWT-like tokens."""

from __future__ import annotations

import base64
import hashlib
import json
import time
import uuid
from typing import Any


class TokenService:
    def __init__(self, secret: str = "default_secret", expiry: int = 3600) -> None:
        self._secret = secret
        self._expiry = expiry
        self._revoked: set[str] = set()

    def create_token(self, payload: dict[str, Any]) -> str:
        header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
        data = {**payload, "iat": time.time(), "exp": time.time() + self._expiry, "jti": str(uuid.uuid4())[:8]}
        body = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
        sig = hashlib.sha256((header + "." + body + "." + self._secret).encode()).hexdigest()[:32]
        return f"{header}.{body}.{sig}"

    def verify_token(self, token: str) -> dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            return {"valid": False, "error": "malformed"}
        if token in self._revoked:
            return {"valid": False, "error": "revoked"}
        header_b64, body_b64, sig = parts
        expected_sig = hashlib.sha256((header_b64 + "." + body_b64 + "." + self._secret).encode()).hexdigest()[:32]
        if sig != expected_sig:
            return {"valid": False, "error": "invalid_signature"}
        try:
            body = json.loads(base64.urlsafe_b64decode(body_b64 + "=="))
        except Exception:
            return {"valid": False, "error": "invalid_payload"}
        if body.get("exp", 0) < time.time():
            return {"valid": False, "error": "expired"}
        return {"valid": True, "payload": body}

    def revoke_token(self, token: str) -> bool:
        self._revoked.add(token)
        return True

    def refresh_token(self, token: str) -> str | None:
        result = self.verify_token(token)
        if result["valid"]:
            payload = result["payload"]
            payload.pop("iat", None)
            payload.pop("exp", None)
            payload.pop("jti", None)
            return self.create_token(payload)
        return None
