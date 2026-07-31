from __future__ import annotations

import logging
from dataclasses import dataclass, field


@dataclass
class Policy:
    """A governance policy with scope and rules."""

    name: str
    scope: str = "*"
    rules: dict[str, str] = field(default_factory=dict)
    enabled: bool = True


class PolicyManager:
    """Stores and evaluates governance policies."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.governance.policy_manager")
        self._policies: dict[str, Policy] = {}

    def add(self, policy: Policy) -> None:
        self._policies[policy.name] = policy

    def remove(self, name: str) -> bool:
        return self._policies.pop(name, None) is not None

    def get(self, name: str) -> Policy | None:
        return self._policies.get(name)

    def list(self, enabled_only: bool = False) -> list[Policy]:
        policies = list(self._policies.values())
        if enabled_only:
            policies = [policy for policy in policies if policy.enabled]
        return policies

    def applies(self, name: str, scope: str) -> bool:
        policy = self._policies.get(name)
        if policy is None or not policy.enabled:
            return False
        return policy.scope == "*" or policy.scope == scope

    def count(self) -> int:
        return len(self._policies)
