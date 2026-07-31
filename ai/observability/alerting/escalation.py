"""Alert escalation."""
from __future__ import annotations

import time
from typing import Any


class EscalationPolicy:
    def __init__(self, name: str, levels: list[dict[str, Any]] = None) -> None:
        self.name = name
        self.levels = levels or []
        self.active = True

class EscalationManager:
    def __init__(self) -> None:
        self._policies: dict[str, EscalationPolicy] = {}
        self._escalations: list[dict[str, Any]] = []
    def add_policy(self, name: str, levels: list[dict[str, Any]]) -> EscalationPolicy:
        policy = EscalationPolicy(name, levels)
        self._policies[name] = policy
        return policy
    def remove_policy(self, name: str) -> bool:
        if name in self._policies:
            del self._policies[name]
            return True
        return False
    def escalate(self, alert: dict[str, Any], policy_name: str) -> dict[str, Any]:
        policy = self._policies.get(policy_name)
        if not policy:
            return {"error": "policy_not_found"}
        escalation = {"alert": alert, "policy": policy_name, "timestamp": time.time(), "level": 0}
        self._escalations.append(escalation)
        return escalation
    def list_policies(self) -> list[dict[str, Any]]:
        return [{"name": p.name, "levels": len(p.levels), "active": p.active} for p in self._policies.values()]
    def get_escalations(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._escalations[-limit:]
