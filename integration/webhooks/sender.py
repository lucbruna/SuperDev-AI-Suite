"""Webhook sender."""

from __future__ import annotations

import time
import uuid
from typing import Any

from .retry import RetryPolicy
from .signature import WebhookSignature


class WebhookSender:
    """Sends webhook payloads to subscriber URLs with HMAC signatures."""

    def __init__(self, secret: str = "dev-secret") -> None:
        self._signer = WebhookSignature(secret)
        self._retry = RetryPolicy()
        self._sent: list[dict[str, Any]] = []

    def send(self, url: str, event_type: str,
             payload: dict[str, Any]) -> dict[str, Any]:
        """Simulates delivery: validates, signs, records a delivery receipt."""
        event_id = str(uuid.uuid4())
        signature = self._signer.sign(payload)
        receipt = {
            "event_id": event_id,
            "url": url,
            "event_type": event_type,
            "signature": signature,
            "delivered": True,
            "attempts": 1,
            "timestamp": time.time(),
        }
        self._sent.append(receipt)
        return receipt

    def deliveries(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._sent[-limit:])

    def count(self) -> int:
        return len(self._sent)
