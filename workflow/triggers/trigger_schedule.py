from __future__ import annotations

import logging
from typing import Any

from .trigger_models import Trigger


class TriggerSchedule:
    """Handles time-based trigger scheduling."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.triggers.schedule")

    def evaluate(self, trigger: Trigger) -> bool:
        cron = trigger.config.get("cron", "")
        self._log.debug("Evaluating schedule %s for %s", cron, trigger.id)
        return True
