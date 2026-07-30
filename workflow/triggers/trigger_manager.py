from __future__ import annotations

import logging
from typing import Any

from .trigger_models import Trigger, TriggerStatus


class TriggerManager:
    """Manages trigger registration and lifecycle."""

    def __init__(self) -> None:
        self._triggers: dict[str, Trigger] = {}
        self._log = logging.getLogger("superdev.workflow.triggers.manager")

    def register(self, trigger: Trigger) -> None:
        trigger.status = TriggerStatus.ACTIVE
        self._triggers[trigger.id] = trigger
        self._log.info("Registered trigger %s (%s)", trigger.id, trigger.name)

    def unregister(self, trigger_id: str) -> None:
        self._triggers.pop(trigger_id, None)

    def get(self, trigger_id: str) -> Trigger | None:
        return self._triggers.get(trigger_id)

    def list_active(self) -> list[Trigger]:
        return [t for t in self._triggers.values() if t.status == TriggerStatus.ACTIVE]

    def pause(self, trigger_id: str) -> None:
        t = self._triggers.get(trigger_id)
        if t:
            t.status = TriggerStatus.INACTIVE

    def resume(self, trigger_id: str) -> None:
        t = self._triggers.get(trigger_id)
        if t:
            t.status = TriggerStatus.ACTIVE
