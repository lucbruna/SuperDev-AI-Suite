from __future__ import annotations

import logging
from typing import Any

from .trigger_models import Trigger, TriggerStatus
from .trigger_evaluator import TriggerEvaluator
from .trigger_actions import TriggerActions
from .trigger_events import TriggerEvents


class TriggerEngine:
    """Central engine for trigger lifecycle."""

    def __init__(self) -> None:
        self._evaluator = TriggerEvaluator()
        self._actions = TriggerActions()
        self._events = TriggerEvents()
        self._log = logging.getLogger("superdev.workflow.triggers")

    def fire(self, trigger: Trigger) -> None:
        trigger.status = TriggerStatus.FIRING
        self._events.emit("trigger.firing", trigger_id=trigger.id)
        try:
            context = self._evaluator.evaluate(trigger)
            self._actions.execute(trigger, context)
            trigger.status = TriggerStatus.COMPLETED
            self._events.emit("trigger.completed", trigger_id=trigger.id)
        except Exception as exc:
            trigger.status = TriggerStatus.FAILED
            trigger.context["error"] = str(exc)
            self._events.emit("trigger.failed", trigger_id=trigger.id, error=str(exc))
            self._log.exception("Trigger %s failed", trigger.id)
