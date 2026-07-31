"""Access control engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time, uuid

class AccessDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    ESCALATE = "escalate"

class AccessRequest:
    def __init__(self, subject: str, resource: str, action: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.request_id = str(uuid.uuid4())[:8]
        self.subject = subject
        self.resource = resource
        self.action = action
        self.context = context or {}
        self.timestamp = time.time()

class AccessControlEngine:
    def __init__(self) -> None:
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._decisions: List[Dict[str, Any]] = []
        self._audit_log: List[Dict[str, Any]] = []
    def add_policy(self, policy_id: str, subject_pattern: str, resource_pattern: str, action: str, effect: AccessDecision) -> None:
        self._policies[policy_id] = {"subject": subject_pattern, "resource": resource_pattern, "action": action, "effect": effect.value}
    def remove_policy(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False
    def evaluate(self, request: AccessRequest) -> AccessDecision:
        for policy in self._policies.values():
            if self._match(policy["subject"], request.subject) and self._match(policy["resource"], request.resource) and self._match(policy["action"], request.action):
                decision = AccessDecision(policy["effect"])
                self._decisions.append({"request_id": request.request_id, "subject": request.subject, "resource": request.resource, "action": request.action, "decision": decision.value, "timestamp": time.time()})
                return decision
        self._audit_log.append({"request_id": request.request_id, "subject": request.subject, "resource": request.resource, "action": request.action, "decision": "default_deny", "timestamp": time.time()})
        return AccessDecision.DENY
    def _match(self, pattern: str, value: str) -> bool:
        if pattern == "*":
            return True
        return value == pattern
    def get_decisions(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._decisions[-limit:]
    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._audit_log[-limit:]
    def list_policies(self) -> List[Dict[str, Any]]:
        return [{"id": k, "subject": v["subject"], "resource": v["resource"], "action": v["action"], "effect": v["effect"]} for k, v in self._policies.items()]
    def stats(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for d in self._decisions:
            counts[d["decision"]] = counts.get(d["decision"], 0) + 1
        return counts
