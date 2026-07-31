"""Data protection."""
from __future__ import annotations

import hashlib
from typing import Any


class DataProtector:
    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []
        self._log: list[dict[str, Any]] = []
    def add_rule(self, name: str, pattern: str, action: str = "redact") -> dict[str, Any]:
        rule = {"name": name, "pattern": pattern, "action": action}
        self._rules.append(rule)
        return rule
    def check(self, data: str) -> dict[str, Any]:
        issues = []
        for rule in self._rules:
            if rule["pattern"].lower() in data.lower():
                issues.append({"rule": rule["name"], "action": rule["action"]})
        return {"safe": len(issues) == 0, "issues": issues}
    def protect(self, data: str) -> str:
        result = data
        for rule in self._rules:
            if rule["action"] == "redact":
                result = result.replace(rule["pattern"], "[REDACTED]")
            elif rule["action"] == "hash":
                h = hashlib.sha256(rule["pattern"].encode()).hexdigest()[:8]
                result = result.replace(rule["pattern"], f"[HASH:{h}]")
        return result
    def log_access(self, data_id: str, user: str, action: str) -> dict[str, Any]:
        entry = {"data_id": data_id, "user": user, "action": action}
        self._log.append(entry)
        return entry
    def get_log(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._log[-limit:]
    def list_rules(self) -> list[dict[str, Any]]:
        return self._rules
    def remove_rule(self, name: str) -> bool:
        original = len(self._rules)
        self._rules = [r for r in self._rules if r["name"] != name]
        return len(self._rules) < original
    def count(self) -> int:
        return len(self._rules)
