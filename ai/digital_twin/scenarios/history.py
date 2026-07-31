"""Scenario history."""

from __future__ import annotations

import time
from typing import Any


class ScenarioHistory:
    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def record(self, scenario_id: str, action: str, details: dict[str, Any] = None) -> dict[str, Any]:
        entry = {"scenario_id": scenario_id, "action": action, "details": details or {}, "timestamp": time.time()}
        self._history.append(entry)
        return entry

    def get(self, scenario_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return [h for h in self._history if h["scenario_id"] == scenario_id][-limit:]

    def get_all(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._history[-limit:]

    def by_action(self, action: str) -> list[dict[str, Any]]:
        return [h for h in self._history if h["action"] == action]

    def count(self) -> int:
        return len(self._history)

    def clear(self) -> int:
        n = len(self._history)
        self._history.clear()
        return n
