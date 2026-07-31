"""Registry of trigger definitions."""

from __future__ import annotations

from typing import Any

from automation.triggers.trigger_models import TriggerDefinition


class TriggerRegistry:
    """Stores trigger definitions by id."""

    def __init__(self) -> None:
        self._triggers: dict[str, TriggerDefinition] = {}

    def register(self, definition: TriggerDefinition) -> None:
        self._triggers[definition.trigger_id] = definition

    def get(self, trigger_id: str) -> TriggerDefinition | None:
        return self._triggers.get(trigger_id)

    def list(self) -> list[str]:
        return list(self._triggers)

    def remove(self, trigger_id: str) -> bool:
        return self._triggers.pop(trigger_id, None) is not None

    def set_enabled(self, trigger_id: str, enabled: bool) -> bool:
        definition = self._triggers.get(trigger_id)
        if definition is None:
            return False
        definition.enabled = enabled
        return True

    def snapshot(self) -> dict[str, int]:
        return {"triggers": len(self._triggers)}
