from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Any


class WebhookSecurity:
    """Webhook signature generation and verification."""

    DEFAULT_ALGORITHM = "sha256"

    def generate_secret(self, length: int = 32) -> str:
        return secrets.token_hex(length)

    def sign(self, payload: bytes, secret: str, algorithm: str = DEFAULT_ALGORITHM) -> str:
        hash_func = getattr(hashlib, algorithm, None)
        if hash_func is None:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        mac = hmac.new(secret.encode("utf-8"), payload, hash_func)
        return base64.b64encode(mac.digest()).decode("ascii")

    def verify(self, payload: bytes, secret: str, signature: str, algorithm: str = DEFAULT_ALGORITHM) -> bool:
        expected = self.sign(payload, secret, algorithm)
        return hmac.compare_digest(expected, signature)

    def verify_request(
        self,
        body: bytes,
        header_signature: str,
        secret: str,
        timestamp: str | None = None,
        tolerance: int = 300,
    ) -> tuple[bool, str]:
        """Verify a webhook request with optional timestamp replay protection."""
        if timestamp:
            import time

            try:
                ts = int(timestamp)
                if abs(time.time() - ts) > tolerance:
                    return False, "Timestamp outside tolerance window"
            except (ValueError, TypeError):
                return False, "Invalid timestamp"

        if not header_signature:
            return False, "Missing signature header"

        if self.verify(body, secret, header_signature):
            return True, "Signature verified"

        # Check alternate algorithms
        for algo in ("sha1", "sha256", "sha512"):
            if algo == self.DEFAULT_ALGORITHM:
                continue
            if self.verify(body, secret, header_signature, algo):
                return True, f"Signature verified with {algo}"

        return False, "Signature mismatch"
