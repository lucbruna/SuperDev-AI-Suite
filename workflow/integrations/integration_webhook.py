from __future__ import annotations

import logging
from typing import Any


class IntegrationWebhook:
    """Handles webhook-based integrations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.integrations.webhook")

    def receive(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._log.info("Webhook received payload")
        return {"status": "received", "size": len(payload)}
