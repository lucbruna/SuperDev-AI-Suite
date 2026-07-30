from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any

from ..api_interfaces import IAPIAuthenticator


class JWTHandler(IAPIAuthenticator):
    """JWT token generation, verification, and management (standard lib only)."""

    SUPPORTED_ALGORITHMS = {"HS256", "HS384", "HS512"}

    def __init__(self, secret: str = "", algorithm: str = "HS256", expiry_minutes: int = 60) -> None:
        self._secret = secret
        self._algorithm = algorithm if algorithm in self.SUPPORTED_ALGORITHMS else "HS256"
        self._expiry_minutes = expiry_minutes
        self._blocked_tokens: set[str] = set()

    def _get_hash_obj(self) -> Any:
        alg_map = {
            "HS256": hashlib.sha256,
            "HS384": hashlib.sha384,
            "HS512": hashlib.sha512,
        }
        return alg_map.get(self._algorithm, hashlib.sha256)

    def _base64url_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    def _base64url_decode(self, data: str) -> bytes:
        padded = data + "=" * (4 - len(data) % 4)
        return base64.urlsafe_b64decode(padded)

    def generate(
        self,
        payload: dict[str, Any],
        secret: str | None = None,
        algorithm: str | None = None,
        expiry_minutes: int | None = None,
    ) -> str:
        secret = secret or self._secret
        algorithm = algorithm or self._algorithm
        expiry = expiry_minutes or self._expiry_minutes

        header = {"alg": algorithm, "typ": "JWT"}
        now = int(time.time())
        full_payload = {
            **payload,
            "iat": now,
            "exp": now + expiry * 60,
        }

        header_b64 = self._base64url_encode(json.dumps(header, separators=(",", ":")).encode())
        payload_b64 = self._base64url_encode(json.dumps(full_payload, separators=(",", ":")).encode())
        signing_input = f"{header_b64}.{payload_b64}"

        hash_fn = self._get_hash_obj()
        signature = hmac.new(secret.encode(), signing_input.encode(), hash_fn).digest()
        sig_b64 = self._base64url_encode(signature)

        return f"{header_b64}.{payload_b64}.{sig_b64}"

    def verify(self, token: str, secret: str | None = None) -> dict[str, Any]:
        secret = secret or self._secret
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return {"valid": False, "error": "Invalid token format"}

            header_b64, payload_b64, sig_b64 = parts
            header = json.loads(self._base64url_decode(header_b64))

            hash_fn = self._get_hash_obj()
            expected_sig = hmac.new(secret.encode(), f"{header_b64}.{payload_b64}".encode(), hash_fn).digest()
            actual_sig = self._base64url_decode(sig_b64)

            if not hmac.compare_digest(expected_sig, actual_sig):
                return {"valid": False, "error": "Invalid signature"}

            payload = json.loads(self._base64url_decode(payload_b64))
            now = time.time()
            if "exp" in payload and payload["exp"] < now:
                return {"valid": False, "error": "Token expired"}
            if "nbf" in payload and payload["nbf"] > now:
                return {"valid": False, "error": "Token not yet valid"}

            if self.is_token_blocked(token):
                return {"valid": False, "error": "Token blocked"}

            return {"valid": True, "payload": payload}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def decode(self, token: str) -> dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        return json.loads(self._base64url_decode(parts[1]))

    def refresh_token(self, old_token: str, secret: str | None = None, new_expiry: int | None = None) -> str | None:
        secret = secret or self._secret
        result = self.verify(old_token, secret)
        if not result.get("valid"):
            return None
        payload = result["payload"]
        payload.pop("exp", None)
        payload.pop("iat", None)
        return self.generate(payload, secret, expiry_minutes=new_expiry or self._expiry_minutes)

    def block_token(self, token: str) -> None:
        self._blocked_tokens.add(token)

    def is_token_blocked(self, token: str) -> bool:
        return token in self._blocked_tokens

    async def authenticate(self, request: Any) -> dict[str, Any]:
        headers = getattr(request, "headers", {})
        auth = headers.get("Authorization", "") if isinstance(headers, dict) else ""
        if auth.startswith("Bearer "):
            token = auth[7:]
            result = self.verify(token)
            if result.get("valid"):
                return {"authenticated": True, "method": "jwt", "user_id": result["payload"].get("sub", "")}
            return {"authenticated": False, "method": "jwt", "error": result.get("error", "Invalid token")}
        return {"authenticated": False, "method": "jwt", "error": "No Bearer token"}

    async def validate_token(self, token: str) -> dict[str, Any]:
        return self.verify(token)

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self._algorithm,
            "expiry_minutes": self._expiry_minutes,
            "blocked_tokens": len(self._blocked_tokens),
            "secret_configured": bool(self._secret),
        }
