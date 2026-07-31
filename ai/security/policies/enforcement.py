"""Policy enforcement."""
from __future__ import annotations

import time
from enum import Enum
from typing import Any


class EnforcementMode(Enum):
    ENFORCING = "enforcing"
    PERMISSIVE = "permissive"
    DISABLED = "disabled"

class EnforcementAction(Enum):
    BLOCK = "block"
    WARN = "warn"
    LOG = "log"
    ESCALATE = "escalate"

class PolicyEnforcer:
    def __init__(self) -> None:
        self._policies: dict[str, dict[str, Any]] = {}
        self._enforcement_log: list[dict[str, Any]] = []
        self._mode = EnforcementMode.ENFORCING
        self._exceptions: set[str] = set()
    def register_policy(self, policy_id: str, name: str, rules: list[dict[str, Any]], action: EnforcementAction = EnforcementAction.BLOCK) -> None:
        self._policies[policy_id] = {"name": name, "rules": rules, "action": action.value, "enabled": True}
    def enforce(self, policy_id: str, context: dict[str, Any]) -> dict[str, Any]:
        if self._mode == EnforcementMode.DISABLED:
            return {"enforced": False, "reason": "mode_disabled"}
        if policy_id in self._exceptions:
            return {"enforced": False, "reason": "exception"}
        policy = self._policies.get(policy_id)
        if not policy or not policy["enabled"]:
            return {"enforced": False, "reason": "policy_not_found"}
        violation = self._check_rules(policy["rules"], context)
        entry = {"policy_id": policy_id, "context": context, "violation": violation, "action": policy["action"], "mode": self._mode.value, "timestamp": time.time()}
        self._enforcement_log.append(entry)
        if violation:
            return {"enforced": True, "violation": violation, "action": policy["action"]}
        return {"enforced": True, "violation": None, "action": "none"}
    def _check_rules(self, rules: list[dict[str, Any]], context: dict[str, Any]) -> str | None:
        for rule in rules:
            key = rule.get("key", "")
            expected = rule.get("expected")
            if key and context.get(key) != expected:
                return f"rule_violated: {key} expected {expected} got {context.get(key)}"
        return None
    def set_mode(self, mode: EnforcementMode) -> None:
        self._mode = mode
    def add_exception(self, policy_id: str) -> None:
        self._exceptions.add(policy_id)
    def remove_exception(self, policy_id: str) -> bool:
        if policy_id in self._exceptions:
            self._exceptions.remove(policy_id)
            return True
        return False
    def get_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._enforcement_log[-limit:]
    def list_policies(self) -> list[dict[str, Any]]:
        return [{"id": k, "name": v["name"], "action": v["action"], "enabled": v["enabled"]} for k, v in self._policies.items()]
