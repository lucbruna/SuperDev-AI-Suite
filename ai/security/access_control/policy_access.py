"""Policy-based access control."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time, uuid

class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"

class AccessPolicy:
    def __init__(self, name: str, effect: PolicyEffect, rules: Optional[List[Dict[str, Any]]] = None) -> None:
        self.policy_id = str(uuid.uuid4())[:8]
        self.name = name
        self.effect = effect
        self.rules = rules or []
        self.priority = 0
        self.enabled = True

class PolicyAccessControl:
    def __init__(self) -> None:
        self._policies: Dict[str, AccessPolicy] = {}
        self._evaluation_log: List[Dict[str, Any]] = []
    def create_policy(self, name: str, effect: PolicyEffect, rules: Optional[List[Dict[str, Any]]] = None) -> AccessPolicy:
        policy = AccessPolicy(name, effect, rules)
        self._policies[policy.policy_id] = policy
        return policy
    def add_rule(self, policy_id: str, rule: Dict[str, Any]) -> bool:
        policy = self._policies.get(policy_id)
        if policy:
            policy.rules.append(rule)
            return True
        return False
    def evaluate(self, context: Dict[str, Any]) -> PolicyEffect:
        applicable = sorted([p for p in self._policies.values() if p.enabled], key=lambda p: -p.priority)
        for policy in applicable:
            if self._match_rules(policy.rules, context):
                self._evaluation_log.append({"policy_id": policy.policy_id, "name": policy.name, "effect": policy.effect.value, "timestamp": time.time()})
                return policy.effect
        return PolicyEffect.DENY
    def _match_rules(self, rules: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        if not rules:
            return True
        for rule in rules:
            key = rule.get("key", "")
            value = rule.get("value")
            if key and context.get(key) != value:
                return False
        return True
    def enable(self, policy_id: str) -> bool:
        policy = self._policies.get(policy_id)
        if policy:
            policy.enabled = True
            return True
        return False
    def disable(self, policy_id: str) -> bool:
        policy = self._policies.get(policy_id)
        if policy:
            policy.enabled = False
            return True
        return False
    def delete_policy(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False
    def list_policies(self) -> List[Dict[str, Any]]:
        return [{"id": p.policy_id, "name": p.name, "effect": p.effect.value, "enabled": p.enabled, "priority": p.priority, "rules_count": len(p.rules)} for p in self._policies.values()]
    def get_evaluation_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._evaluation_log[-limit:]
