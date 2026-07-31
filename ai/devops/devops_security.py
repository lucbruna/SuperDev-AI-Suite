"""DevOps security."""
from __future__ import annotations

from typing import Any


class DevOpsSecurity:
    def __init__(self) -> None:
        self._policies: dict[str, dict[str, Any]] = {}
        self._audit_log: list[dict[str, Any]] = []
    def add_policy(self, name: str, rules: dict[str, Any]) -> dict[str, Any]:
        policy = {"name": name, "rules": rules, "active": True}
        self._policies[name] = policy
        return policy
    def check(self, action: str, context: dict[str, Any] = None) -> dict[str, Any]:
        for policy in self._policies.values():
            if not policy["active"]:
                continue
            if action in policy["rules"].get("blocked", []):
                return {"allowed": False, "policy": policy["name"]}
        return {"allowed": True}
    def log_access(self, user: str, action: str, resource: str) -> dict[str, Any]:
        entry = {"user": user, "action": action, "resource": resource}
        self._audit_log.append(entry)
        return entry
    def list_policies(self) -> list[str]:
        return list(self._policies.keys())
    def get_audit_log(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._audit_log[-limit:]
