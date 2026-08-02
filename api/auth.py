from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Any, Callable


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


class JWTHandler:
    """Stateless HMAC-signed JWT encode/decode helper."""

    def __init__(self, secret: str = "") -> None:
        self._secret = secret or "super-dev-default-secret"

    def encode(self, payload: dict[str, Any], ttl: int = 3600) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        now = int(time.time())
        body = dict(payload)
        body["iat"] = now
        body["exp"] = now + ttl
        header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        body_part = _b64url_encode(json.dumps(body, separators=(",", ":")).encode("utf-8"))
        signing_input = f"{header_part}.{body_part}".encode("utf-8")
        signature = _b64url_encode(hmac.new(self._secret.encode("utf-8"), signing_input, hashlib.sha256).digest())
        return f"{header_part}.{body_part}.{signature}"

    def decode(self, token: str) -> dict[str, Any] | None:
        try:
            header_part, body_part, signature = token.split(".")
        except ValueError:
            return None
        signing_input = f"{header_part}.{body_part}".encode("utf-8")
        expected = _b64url_encode(hmac.new(self._secret.encode("utf-8"), signing_input, hashlib.sha256).digest())
        if not hmac.compare_digest(expected, signature):
            return None
        try:
            payload = json.loads(_b64url_decode(body_part))
        except (ValueError, json.JSONDecodeError):
            return None
        exp = payload.get("exp")
        if exp is not None and int(exp) <= int(time.time()):
            return None
        return payload


class APIKeyHandler:
    """Issues and validates opaque API keys for users."""

    def __init__(self) -> None:
        self._keys: dict[str, str] = {}

    def generate(self, user_id: str) -> str:
        api_key = "key_" + hashlib.sha256(f"{user_id}:{uuid.uuid4()}".encode("utf-8")).hexdigest()
        self._keys[api_key] = user_id
        return api_key

    def validate(self, api_key: str) -> str | None:
        return self._keys.get(api_key)


class MFAHandler:
    """TOTP-style code generation and verification."""

    def generate_secret(self) -> str:
        return base64.b32encode(uuid.uuid4().bytes).decode("ascii").rstrip("=")

    def generate_code(self, secret: str) -> str:
        digest = hashlib.sha1(f"{secret}:{int(time.time()) // 30}".encode("utf-8")).digest()
        offset = digest[-1] & 0x0F
        code = (int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFFFFFF) % 1_000_000
        return f"{code:06d}"

    def verify_code(self, secret: str, code: str) -> bool:
        return self.generate_code(secret) == code


class SessionHandler:
    """In-memory session store with create/validate/invalidate."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def create(self, user_id: str) -> dict[str, Any]:
        session_id = str(uuid.uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "expires_at": time.time() + 3600,
        }
        self._sessions[session_id] = session
        return session

    def validate(self, session_id: str) -> dict[str, Any] | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session["expires_at"] <= time.time():
            self._sessions.pop(session_id, None)
            return None
        return session

    def invalidate(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


class Authenticator:
    """Pluggable authentication facade."""

    def __init__(self) -> None:
        self.plugins: dict[str, Any] = {}

    def register(self, name: str, handler: Any) -> None:
        self.plugins[name] = handler

    def get(self, name: str) -> Any | None:
        return self.plugins.get(name)

    async def authenticate(self, request: Any) -> dict[str, Any]:
        for handler in self.plugins.values():
            authenticate = getattr(handler, "authenticate", None) or getattr(handler, "validate", None)
            if authenticate is None:
                continue
            try:
                result = authenticate(request)
                if hasattr(result, "__await__"):
                    result = await result
            except Exception:
                continue
            if result:
                return {"authenticated": True, "result": result}
        return {"authenticated": False}


class OAuthHandler:
    """OAuth-style token issuance and validation."""

    def __init__(self, client_id: str = "", client_secret: str = "") -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._tokens: dict[str, str] = {}

    def authorize(self, user_id: str) -> str:
        token = str(uuid.uuid4())
        self._tokens[token] = user_id
        return token

    def validate(self, token: str) -> str | None:
        return self._tokens.get(token)

    def revoke(self, token: str) -> None:
        self._tokens.pop(token, None)
