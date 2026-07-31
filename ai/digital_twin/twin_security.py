"""Digital Twin security."""
from __future__ import annotations
from typing import Any, Dict, List

class TwinSecurity:
    def __init__(self) -> None:
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._audit_log: List[Dict[str, Any]] = []
    def add_policy(self, name: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        policy = {"name": name, "rules": rules, "active": True}
        self._policies[name] = policy
        return policy
    def check(self, action: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        for policy in self._policies.values():
            if not policy["active"]:
                continue
            if action in policy["rules"].get("blocked", []):
                return {"allowed": False, "policy": policy["name"]}
        return {"allowed": True}
    def log_access(self, user: str, action: str, resource: str) -> Dict[str, Any]:
        entry = {"user": user, "action": action, "resource": resource}
        self._audit_log.append(entry)
        return entry
    def list_policies(self) -> List[str]:
        return list(self._policies.keys())
    def get_audit_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._audit_log[-limit:]
    def disable_policy(self, name: str) -> bool:
        if name in self._policies:
            self._policies[name]["active"] = False
            return True
        return False
