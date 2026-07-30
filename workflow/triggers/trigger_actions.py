from __future__ import annotations

import logging
from typing import Any

from .trigger_models import Trigger


class TriggerActions:
    """Executes actions associated with a trigger."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.triggers.actions")

    def execute(self, trigger: Trigger, context: dict[str, Any]) -> None:
        action = trigger.config.get("action", "")
        self._log.info("Executing action %s for trigger %s", action, trigger.id)
        trigger.context["action_result"] = {"action": action, "status": "executed"}
