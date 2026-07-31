"""Cache invalidation."""
from __future__ import annotations

import time
from typing import Any


class InvalidationManager:
    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []
        self._history: list[dict[str, Any]] = []
    def add_rule(self, pattern: str, strategy: str = "delete", description: str = "") -> dict[str, Any]:
        rule = {"pattern": pattern, "strategy": strategy, "description": description, "created_at": time.time(), "active": True}
        self._rules.append(rule)
        return rule
    def remove_rule(self, pattern: str) -> bool:
        original = len(self._rules)
        self._rules = [r for r in self._rules if r["pattern"] != pattern]
        return len(self._rules) < original
    def check(self, key: str) -> dict[str, Any]:
        for rule in self._rules:
            if rule["active"] and rule["pattern"] in key:
                self._history.append({"key": key, "rule": rule["pattern"], "strategy": rule["strategy"], "timestamp": time.time()})
                return {"invalidate": True, "strategy": rule["strategy"], "rule": rule["pattern"]}
        return {"invalidate": False}
    def execute(self, cache, key: str) -> dict[str, Any]:
        check = self.check(key)
        if not check["invalidate"]:
            return {"action": "none"}
        strategy = check["strategy"]
        if strategy == "delete":
            cache.delete(key)
            return {"action": "deleted", "key": key}
        elif strategy == "refresh":
            cache.delete(key)
            return {"action": "refreshed", "key": key}
        return {"action": "skipped"}
    def list_rules(self) -> list[dict[str, Any]]:
        return self._rules
    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._history[-limit:]
    def clear_rules(self) -> int:
        n = len(self._rules)
        self._rules.clear()
        return n
