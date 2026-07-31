"""Limit policies."""
from __future__ import annotations

from typing import Any


class LimitPolicies:
    def __init__(self) -> None:
        self._policies: dict[str, dict[str, Any]] = {}
    def create(self, name: str, resource: str, limit: float, period: str = "monthly", action: str = "block") -> dict[str, Any]:
        policy = {"name": name, "resource": resource, "limit": limit, "period": period, "action": action, "active": True}
        self._policies[name] = policy
        return policy
    def get(self, name: str) -> dict[str, Any]:
        return self._policies.get(name, {})
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._policies.values())
    def list_by_resource(self, resource: str) -> list[dict[str, Any]]:
        return [p for p in self._policies.values() if p["resource"] == resource]
    def deactivate(self, name: str) -> bool:
        if name in self._policies:
            self._policies[name]["active"] = False
            return True
        return False
    def activate(self, name: str) -> bool:
        if name in self._policies:
            self._policies[name]["active"] = True
            return True
        return False
    def delete(self, name: str) -> bool:
        if name in self._policies:
            del self._policies[name]
            return True
        return False
    def evaluate(self, resource: str, usage: float) -> dict[str, Any]:
        for policy in self._policies.values():
            if policy["resource"] == resource and policy["active"] and usage >= policy["limit"]:
                return {"policy": policy["name"], "exceeded": True, "action": policy["action"]}
        return {"exceeded": False}
