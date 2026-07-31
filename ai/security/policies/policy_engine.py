"""Policy engine."""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import time, uuid

class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    LOG = "log"

class Policy:
    def __init__(self, name: str, effect: PolicyEffect, description: str = "") -> None:
        self.policy_id = str(uuid.uuid4())[:8]
        self.name = name
        self.effect = effect
        self.description = description
        self.enabled = True
        self.created_at = time.time()
        self.conditions: Dict[str, Any] = {}
        self.priority = 0

class PolicyEngine:
    def __init__(self) -> None:
        self._policies: Dict[str, Policy] = {}
        self._evaluation_log: List[Dict[str, Any]] = []
    def create_policy(self, name: str, effect: PolicyEffect, description: str = "") -> Policy:
        policy = Policy(name, effect, description)
        self._policies[policy.policy_id] = policy
        return policy
    def add_condition(self, policy_id: str, key: str, value: Any) -> bool:
        policy = self._policies.get(policy_id)
        if policy:
            policy.conditions[key] = value
            return True
        return False
    def evaluate(self, context: Dict[str, Any]) -> PolicyEffect:
        applicable = sorted([p for p in self._policies.values() if p.enabled], key=lambda p: -p.priority)
        for policy in applicable:
            match = all(context.get(k) == v for k, v in policy.conditions.items()) if policy.conditions else True
            if match:
                self._evaluation_log.append({"policy_id": policy.policy_id, "name": policy.name, "effect": policy.effect.value, "context": context, "timestamp": time.time()})
                return policy.effect
        return PolicyEffect.DENY
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
        return [{"id": p.policy_id, "name": p.name, "effect": p.effect.value, "enabled": p.enabled, "priority": p.priority} for p in self._policies.values()]
    def get_evaluation_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._evaluation_log[-limit:]
