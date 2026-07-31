"""
Policy Engine
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass
class PolicyStatement:
    effect: PolicyEffect
    actions: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    conditions: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDocument:
    name: str
    version: str = "1.0"
    statements: list[PolicyStatement] = field(default_factory=list)
    enabled: bool = True


class PolicyEngine:
    def __init__(self):
        self.policies: dict[str, PolicyDocument] = {}

    def add_policy(self, policy: PolicyDocument) -> None:
        self.policies[policy.name] = policy

    def get_policy(self, name: str) -> PolicyDocument | None:
        return self.policies.get(name)

    def remove_policy(self, name: str) -> bool:
        if name in self.policies:
            del self.policies[name]
            return True
        return False

    def evaluate(self, action: str, resource: str, context: dict[str, Any] = None) -> PolicyEffect:
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            for statement in policy.statements:
                if self._matches_statement(statement, action, resource, context or {}):
                    return statement.effect
        return PolicyEffect.DENY

    def _matches_statement(self, statement: PolicyStatement, action: str, resource: str, context: dict) -> bool:
        if statement.actions and action not in statement.actions:
            return False
        if statement.resources and resource not in statement.resources:
            return False
        for key, value in statement.conditions.items():
            if key not in context:
                return False
            if isinstance(value, list):
                if context[key] not in value:
                    return False
            elif context[key] != value:
                return False
        return True

    def is_allowed(self, action: str, resource: str, context: dict[str, Any] = None) -> bool:
        return self.evaluate(action, resource, context) == PolicyEffect.ALLOW

    def list_policies(self) -> list[PolicyDocument]:
        return list(self.policies.values())

    def count(self) -> int:
        return len(self.policies)
