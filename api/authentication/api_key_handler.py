from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from typing import Any

from ..api_interfaces import IAPIAuthenticator


class APIKeyHandler(IAPIAuthenticator):
    """API key generation, hashing, and validation."""

    def __init__(self, key_prefix: str = "sk-") -> None:
        self._key_prefix = key_prefix
        self._api_keys: dict[str, dict[str, Any]] = {}
        self._hashed_keys: dict[str, str] = {}

    def generate_key(self, prefix: str | None = None, entropy_bytes: int = 32) -> str:
        prefix = prefix or self._key_prefix
        random_bytes = secrets.token_bytes(entropy_bytes)
        key = prefix + secrets.token_hex(entropy_bytes)
        return key

    def hash_key(self, key: str) -> str:
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac("sha256", key.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"

    def verify_key(self, key: str, hashed_key: str) -> bool:
        try:
            salt, stored_hash = hashed_key.split("$", 1)
            computed = hashlib.pbkdf2_hmac("sha256", key.encode(), salt.encode(), 100000)
            return hmac.compare_digest(computed.hex(), stored_hash)
        except (ValueError, IndexError):
            return False

    def register_key(self, key: str, metadata: dict[str, Any] | None = None) -> str:
        hashed = self.hash_key(key)
        key_id = f"key_{secrets.token_hex(8)}"
        self._api_keys[key_id] = {
            "hashed_key": hashed,
            "metadata": metadata or {},
            "active": True,
        }
        return key_id

    def validate(self, key: str) -> dict[str, Any]:
        for key_id, key_data in self._api_keys.items():
            if not key_data["active"]:
                continue
            if self.verify_key(key, key_data["hashed_key"]):
                return {
                    "valid": True,
                    "key_id": key_id,
                    "metadata": key_data["metadata"],
                }
        return {"valid": False, "error": "Invalid API key"}

    def revoke_key(self, key_id: str) -> bool:
        if key_id in self._api_keys:
            self._api_keys[key_id]["active"] = False
            return True
        return False

    async def authenticate(self, request: Any) -> dict[str, Any]:
        headers = getattr(request, "headers", {}) if hasattr(request, "headers") else request.get("headers", {})
        api_key = ""
        if isinstance(headers, dict):
            api_key = headers.get("x-api-key", headers.get("X-API-Key", ""))
        if api_key:
            result = self.validate(api_key)
            if result.get("valid"):
                return {"authenticated": True, "method": "api_key", **result}
            return {"authenticated": False, "method": "api_key", "error": result.get("error", "Invalid")}
        return {"authenticated": False, "method": "api_key", "error": "No API key provided"}

    async def validate_token(self, token: str) -> dict[str, Any]:
        return self.validate(token)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_prefix": self._key_prefix,
            "registered_keys": len(self._api_keys),
        }
