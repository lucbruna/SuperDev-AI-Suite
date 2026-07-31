"""Limit enforcement."""
from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any


class LimitEnforcer:
    def __init__(self) -> None:
        self._policies: dict[str, dict[str, Any]] = {}
        self._violations: list[dict[str, Any]] = []
    def add_policy(self, resource: str, limit: float, action: str = "block", callback: Callable = None) -> None:
        self._policies[resource] = {"limit": limit, "action": action, "callback": callback}
    def check(self, org_id: str, resource: str, current_usage: float) -> dict[str, Any]:
        policy = self._policies.get(resource)
        if not policy:
            return {"allowed": True, "reason": "no_policy"}
        if current_usage >= policy["limit"]:
            violation = {"org_id": org_id, "resource": resource, "usage": current_usage, "limit": policy["limit"], "action": policy["action"]}
            self._violations.append(violation)
            if policy.get("callback"):
                with contextlib.suppress(Exception):
                    policy["callback"](violation)
            return {"allowed": False, "reason": "limit_exceeded", "action": policy["action"]}
        return {"allowed": True, "reason": "within_limit"}
    def get_violations(self, org_id: str = "", resource: str = "", limit: int = 50) -> list[dict[str, Any]]:
        results = self._violations
        if org_id:
            results = [v for v in results if v["org_id"] == org_id]
        if resource:
            results = [v for v in results if v["resource"] == resource]
        return results[-limit:]
    def list_policies(self) -> dict[str, dict[str, Any]]:
        return {k: {"limit": v["limit"], "action": v["action"]} for k, v in self._policies.items()}
    def remove_policy(self, resource: str) -> bool:
        if resource in self._policies:
            del self._policies[resource]
            return True
        return False
    def clear_violations(self) -> int:
        n = len(self._violations)
        self._violations.clear()
        return n
