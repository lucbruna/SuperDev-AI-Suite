"""Webhook receiver."""

from __future__ import annotations

from typing import Any, Callable

from .signature import WebhookSignature
from .validator import WebhookValidator


class WebhookReceiver:
    """Receives and dispatches webhook events to registered handlers."""

    def __init__(self, secret: str = "dev-secret") -> None:
        self._signer = WebhookSignature(secret)
        self.validator = WebhookValidator()
        self._handlers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}
        self._received: list[dict[str, Any]] = []

    def on(self, event_type: str, handler: Callable[[dict[str, Any]], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def handle(self, event_type: str, payload: dict[str, Any],
               signature: str) -> bool:
        if not self._signer.verify(payload, signature):
            return False
        errors = self.validator.validate(event_type, payload)
        if errors:
            return False
        self._received.append({"event_type": event_type, "payload": payload})
        for handler in self._handlers.get(event_type, []):
            handler(payload)
        return True

    def received(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._received[-limit:])

    def count(self) -> int:
        return len(self._received)
