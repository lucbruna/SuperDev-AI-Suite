"""Policies: declarative governance rules with optional runtime conditions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

EFFECTS = ("allow", "deny")
#: rule condition: (context) -> bool
RuleCondition = Callable[[dict[str, Any]], bool]


@dataclass
class PolicyRule:
    rule_id: str
    effect: str
    actions: list[str] = field(default_factory=list)  # exact names or "*"
    resources: list[str] = field(default_factory=list)  # exact names or "*"
    condition: Optional[RuleCondition] = None

    def matches(self, action: str, resource: str, context: dict[str, Any]) -> bool:
        if self.effect not in EFFECTS:
            return False
        if self.actions and "*" not in self.actions and action not in self.actions:
            return False
        if self.resources and "*" not in self.resources and resource not in self.resources:
            return False
        if self.condition is not None:
            try:
                if not self.condition(context):
                    return False
            except Exception:  # noqa: BLE001 - failing conditions do not match
                return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "effect": self.effect,
            "actions": list(self.actions),
            "resources": list(self.resources),
        }


@dataclass
class Policy:
    policy_id: str
    name: str = ""
    scope: str = "global"
    rules: list[PolicyRule] = field(default_factory=list)
    enabled: bool = True
    version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "scope": self.scope,
            "enabled": self.enabled,
            "version": self.version,
            "rules": [rule.to_dict() for rule in self.rules],
        }
