"""Policy definition."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time, uuid

class PolicyType(Enum):
    SECURITY = "security"
    DATA = "data"
    ACCESS = "access"
    NETWORK = "network"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"

class PolicyDefinition:
    def __init__(self, name: str, policy_type: PolicyType, rules: Optional[List[Dict[str, Any]]] = None) -> None:
        self.policy_id = str(uuid.uuid4())[:8]
        self.name = name
        self.type = policy_type
        self.rules: List[Dict[str, Any]] = rules if rules is not None else []
        self.version = 1
        self.created_at = time.time()
        self.updated_at = time.time()
        self.status = "draft"

class PolicyDefinitionManager:
    def __init__(self) -> None:
        self._policies: Dict[str, PolicyDefinition] = {}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}
    def create(self, name: str, policy_type: PolicyType, rules: Optional[List[Dict[str, Any]]] = None) -> PolicyDefinition:
        policy = PolicyDefinition(name, policy_type, rules)
        self._policies[policy.policy_id] = policy
        self._versions[policy.policy_id] = [{"version": 1, "rules": policy.rules, "timestamp": time.time()}]
        return policy
    def add_rule(self, policy_id: str, rule: Dict[str, Any]) -> bool:
        policy = self._policies.get(policy_id)
        if policy:
            policy.rules.append(rule)
            policy.version += 1
            policy.updated_at = time.time()
            self._versions.setdefault(policy_id, []).append({"version": policy.version, "rules": list(policy.rules), "timestamp": time.time()})
            return True
        return False
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        policy = self._policies.get(policy_id)
        if policy:
            return {"id": policy.policy_id, "name": policy.name, "type": policy.type.value, "version": policy.version, "status": policy.status, "rules_count": len(policy.rules)}
        return None
    def list_policies(self, policy_type: Optional[PolicyType] = None) -> List[str]:
        if policy_type:
            return [p.policy_id for p in self._policies.values() if p.type == policy_type]
        return list(self._policies.keys())
    def get_versions(self, policy_id: str) -> List[Dict[str, Any]]:
        return self._versions.get(policy_id, [])
    def approve(self, policy_id: str) -> bool:
        policy = self._policies.get(policy_id)
        if policy:
            policy.status = "active"
            return True
        return False
    def retire(self, policy_id: str) -> bool:
        policy = self._policies.get(policy_id)
        if policy:
            policy.status = "retired"
            return True
        return False
