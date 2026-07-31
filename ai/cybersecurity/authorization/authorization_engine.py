"""
Authorization Engine
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AccessDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"


@dataclass
class AccessRequest:
    user_id: str
    resource: str
    action: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessPolicy:
    name: str
    effect: str = "allow"
    actions: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    conditions: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    enabled: bool = True


class AuthorizationEngine:
    def __init__(self):
        self.policies: list[AccessPolicy] = []

    def add_policy(self, policy: AccessPolicy) -> None:
        self.policies.append(policy)
        self.policies.sort(key=lambda p: p.priority, reverse=True)

    def evaluate(self, request: AccessRequest) -> AccessDecision:
        for policy in self.policies:
            if not policy.enabled:
                continue
            if self._matches_policy(policy, request):
                return AccessDecision.ALLOW if policy.effect == "allow" else AccessDecision.DENY
        return AccessDecision.DENY

    def _matches_policy(self, policy: AccessPolicy, request: AccessRequest) -> bool:
        if policy.actions and request.action not in policy.actions:
            return False
        if policy.resources and request.resource not in policy.resources:
            return False
        for key, value in policy.conditions.items():
            if key not in request.context:
                return False
            if isinstance(value, list):
                if request.context[key] not in value:
                    return False
            elif request.context[key] != value:
                return False
        return True

    def check_access(self, user_id: str, resource: str, action: str, context: dict = None) -> bool:
        request = AccessRequest(user_id=user_id, resource=resource, action=action, context=context or {})
        decision = self.evaluate(request)
        return decision == AccessDecision.ALLOW

    def remove_policy(self, name: str) -> bool:
        for i, p in enumerate(self.policies):
            if p.name == name:
                self.policies.pop(i)
                return True
        return False

    def list_policies(self) -> list[AccessPolicy]:
        return self.policies.copy()
