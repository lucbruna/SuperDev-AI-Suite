"""Scenario history."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ScenarioHistory:
    def __init__(self) -> None:
        self._history: List[Dict[str, Any]] = []
    def record(self, scenario_id: str, action: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        entry = {"scenario_id": scenario_id, "action": action, "details": details or {}, "timestamp": time.time()}
        self._history.append(entry)
        return entry
    def get(self, scenario_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return [h for h in self._history if h["scenario_id"] == scenario_id][-limit:]
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def by_action(self, action: str) -> List[Dict[str, Any]]:
        return [h for h in self._history if h["action"] == action]
    def count(self) -> int:
        return len(self._history)
    def clear(self) -> int:
        n = len(self._history)
        self._history.clear()
        return n
