"""ABAC (Attribute-Based Access Control)."""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import time, uuid

class ABACEffect(Enum):
    PERMIT = "permit"
    DENY = "deny"
    NOT_APPLICABLE = "not_applicable"
    INDETERMINATE = "indeterminate"

class ABACPolicy:
    def __init__(self, name: str, target: Dict[str, Any], effect: ABACEffect) -> None:
        self.policy_id = str(uuid.uuid4())[:8]
        self.name = name
        self.target = target
        self.effect = effect
        self.obligations: List[str] = []
        self.enabled = True

class ABACEngine:
    def __init__(self) -> None:
        self._policies: Dict[str, ABACPolicy] = {}
        self._decisions: List[Dict[str, Any]] = []
        self._attribute_providers: Dict[str, Callable[..., Any]] = {}
    def add_policy(self, name: str, target: Dict[str, Any], effect: ABACEffect) -> ABACPolicy:
        policy = ABACPolicy(name, target, effect)
        self._policies[policy.policy_id] = policy
        return policy
    def remove_policy(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False
    def register_attribute_provider(self, name: str, provider: Callable[..., Any]) -> None:
        self._attribute_providers[name] = provider
    def evaluate(self, subject: Dict[str, Any], resource: Dict[str, Any], action: str, environment: Optional[Dict[str, Any]] = None) -> ABACEffect:
        context = {"subject": subject, "resource": resource, "action": action, "environment": environment or {}}
        for policy in sorted(self._policies.values(), key=lambda p: p.policy_id):
            if not policy.enabled:
                continue
            if self._match_target(policy.target, context):
                decision = policy.effect
                self._decisions.append({"policy_id": policy.policy_id, "name": policy.name, "effect": decision.value, "context": context, "timestamp": time.time()})
                return decision
        self._decisions.append({"policy_id": None, "name": "default", "effect": ABACEffect.DENY.value, "context": context, "timestamp": time.time()})
        return ABACEffect.DENY
    def _match_target(self, target: Dict[str, Any], context: Dict[str, Any]) -> bool:
        for key, value in target.items():
            parts = key.split(".")
            current = context
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return False
            if current != value:
                return False
        return True
    def get_decisions(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._decisions[-limit:]
    def list_policies(self) -> List[Dict[str, Any]]:
        return [{"id": p.policy_id, "name": p.name, "effect": p.effect.value, "target": p.target, "enabled": p.enabled} for p in self._policies.values()]
