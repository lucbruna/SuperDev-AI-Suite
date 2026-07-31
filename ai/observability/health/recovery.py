"""Health recovery."""
from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class RecoveryManager:
    def __init__(self) -> None:
        self._strategies: dict[str, Callable[[], bool]] = {}
        self._history: list[dict[str, Any]] = []
    def add_strategy(self, component: str, recovery_func: Callable[[], bool]) -> None:
        self._strategies[component] = recovery_func
    def recover(self, component: str) -> dict[str, Any]:
        strategy = self._strategies.get(component)
        if not strategy:
            return {"component": component, "status": "no_strategy"}
        try:
            success = strategy()
            entry = {"component": component, "success": success, "timestamp": time.time()}
        except Exception as e:
            entry = {"component": component, "success": False, "error": str(e), "timestamp": time.time()}
        self._history.append(entry)
        return entry
    def get_history(self, component: str = "", limit: int = 50) -> list[dict[str, Any]]:
        results = self._history
        if component:
            results = [h for h in results if h["component"] == component]
        return results[-limit:]
    def list_strategies(self) -> list[str]:
        return list(self._strategies.keys())
    def remove_strategy(self, component: str) -> bool:
        if component in self._strategies:
            del self._strategies[component]
            return True
        return False
