"""Trigger Manager — named triggers that fire on studio events."""
from __future__ import annotations

from typing import Any


class TriggerManager:
    """Registers event triggers and reports their state."""

    def __init__(self) -> None:
        self._triggers: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, event: str = "video.ready",
                 action: str = "notify") -> dict[str, Any]:
        self._triggers[name] = {"name": name, "event": event, "action": action, "active": True}
        return {"registered": name, "event": event, "active": True}

    def list(self) -> dict[str, Any]:
        return {"triggers": list(self._triggers.values()), "count": len(self._triggers)}


_trigger_manager: TriggerManager | None = None


def get_trigger_manager() -> TriggerManager:
    global _trigger_manager
    if _trigger_manager is None:
        _trigger_manager = TriggerManager()
    return _trigger_manager
