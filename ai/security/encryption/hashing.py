"""Hashing utilities."""

from __future__ import annotations

import hashlib
import hmac
import secrets


class HashService:
    """Digest/salted-hash/HMAC helpers (SHA-256 based, constant-time verify)."""

    def __init__(self) -> None:
        self._algo = "sha256"

    def hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def hash_with_salt(self, data: str, salt: str = "") -> dict[str, str]:
        s = salt or secrets.token_hex(16)
        h = hashlib.sha256((data + s).encode()).hexdigest()
        return {"hash": h, "salt": s}

    def verify(self, data: str, expected_hash: str, salt: str = "") -> bool:
        result = self.hash_with_salt(data, salt)
        return hmac.compare_digest(result["hash"], expected_hash)

    def hmac_sign(self, data: str, secret: str) -> str:
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

    def hmac_verify(self, data: str, signature: str, secret: str) -> bool:
        expected = self.hmac_sign(data, secret)
        return hmac.compare_digest(signature, expected)

    def file_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def quick_hash(self, data: str) -> str:
        """Non-cryptographic fast digest (MD5) for cache keys/dedup — NOT for security.

        Use :meth:`hash`/:meth:`hash_with_salt` or :meth:`hmac_sign` for integrity/auth.
        """
        return hashlib.md5(data.encode()).hexdigest()
