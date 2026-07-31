"""Emergency mode."""

from __future__ import annotations

import time
from typing import Any


class EmergencyMode:
    def __init__(self) -> None:
        self._active = False
        self._history: list[dict[str, Any]] = []

    def activate(self, reason: str = "") -> dict[str, Any]:
        self._active = True
        entry = {"action": "activated", "reason": reason, "timestamp": time.time()}
        self._history.append(entry)
        return entry

    def deactivate(self) -> dict[str, Any]:
        self._active = False
        entry = {"action": "deactivated", "timestamp": time.time()}
        self._history.append(entry)
        return entry

    def is_active(self) -> bool:
        return self._active

    def get_status(self) -> dict[str, Any]:
        return {"active": self._active}

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._history[-limit:]

    def count(self) -> int:
        return len(self._history)
