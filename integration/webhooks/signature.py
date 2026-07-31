"""Webhook signature verification (HMAC)."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any


class WebhookSignature:
    """Signs and verifies webhook payloads with HMAC-SHA256."""

    def __init__(self, secret: str) -> None:
        self._secret = secret.encode("utf-8")

    def sign(self, payload: Any) -> str:
        body = self._serialize(payload)
        digest = hmac.new(self._secret, body, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def verify(self, payload: Any, signature: str) -> bool:
        expected = self.sign(payload)
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def _serialize(payload: Any) -> bytes:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, str):
            return payload.encode("utf-8")
        import json

        return json.dumps(payload, sort_keys=True).encode("utf-8")
