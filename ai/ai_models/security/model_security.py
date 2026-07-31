"""Model security engine."""
from __future__ import annotations
from typing import Any, Dict, List
import time
import hashlib

class ModelSecurity:
    def __init__(self) -> None:
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._violations: List[Dict[str, Any]] = []
    def add_policy(self, name: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        policy = {"name": name, "rules": rules, "created_at": time.time(), "active": True}
        self._policies[name] = policy
        return policy
    def check(self, model_id: str, action: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        for policy in self._policies.values():
            if not policy["active"]:
                continue
            rules = policy["rules"]
            if action in rules.get("blocked_actions", []):
                self._violations.append({"model_id": model_id, "action": action, "policy": policy["name"], "timestamp": time.time()})
                return {"allowed": False, "reason": f"blocked by policy {policy['name']}", "policy": policy["name"]}
        return {"allowed": True}
    def get_violations(self, model_id: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        violations = self._violations
        if model_id:
            violations = [v for v in violations if v["model_id"] == model_id]
        return violations[-limit:]
    def list_policies(self) -> List[str]:
        return list(self._policies.keys())
    def disable_policy(self, name: str) -> bool:
        if name in self._policies:
            self._policies[name]["active"] = False
            return True
        return False
    def enable_policy(self, name: str) -> bool:
        if name in self._policies:
            self._policies[name]["active"] = True
            return True
        return False
    def violation_count(self) -> int:
        return len(self._violations)
    def clear_violations(self) -> int:
        n = len(self._violations)
        self._violations.clear()
        return n
