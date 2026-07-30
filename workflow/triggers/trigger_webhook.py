from __future__ import annotations

import json
import logging
from typing import Any

from .trigger_models import Trigger


class TriggerWebhook:
    """Handles webhook-based triggers."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.triggers.webhook")

    def handle(self, trigger: Trigger, payload: dict[str, Any]) -> dict[str, Any]:
        self._log.info("Webhook trigger %s received payload", trigger.id)
        trigger.context["webhook_payload"] = payload
        return {"status": "received", "trigger_id": trigger.id}
