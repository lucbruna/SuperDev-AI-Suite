"""Webhook engine: facades over receiver, sender, validator, and history."""

from __future__ import annotations

import logging
from typing import Any

from .history import WebhookHistory
from .receiver import WebhookReceiver
from .retry import RetryPolicy, RetryManager
from .sender import WebhookSender
from .validator import WebhookValidator


class WebhookEngine:
    """Facade for the webhook subsystem."""

    def __init__(self, secret: str = "dev-secret") -> None:
        self._log = logging.getLogger("superdev.integration.webhooks")
        self.receiver = WebhookReceiver(secret)
        self.sender = WebhookSender(secret)
        self.validator = WebhookValidator()
        self.history = WebhookHistory()
        self.retry = RetryManager(RetryPolicy())

    def register(self, event_type: str, schema: dict[str, str] | None = None) -> None:
        if schema:
            self.validator.register_schema(event_type, schema)
            self.receiver.validator.register_schema(event_type, schema)
        self._log.info("registered webhook for %s", event_type)

    def dispatch(self, event_type: str, payload: dict[str, Any],
                 signature: str) -> bool:
        """Verifies an inbound webhook and dispatches to handlers."""
        accepted = self.receiver.handle(event_type, payload, signature)
        self.history.record(
            event_type, "accepted" if accepted else "rejected", 1,
            None if accepted else "signature or schema validation failed",
        )
        return accepted

    def notify(self, url: str, event_type: str,
               payload: dict[str, Any]) -> dict[str, Any]:
        """Sends an outbound webhook notification."""
        receipt = self.sender.send(url, event_type, payload)
        self.history.record(receipt["event_id"], "delivered", 1)
        return receipt

    def stats(self) -> dict[str, Any]:
        return {
            "received": self.receiver.count(),
            "sent": self.sender.count(),
            "accepted": self.history.count("accepted"),
            "rejected": self.history.count("rejected"),
            "delivered": self.history.count("delivered"),
        }
