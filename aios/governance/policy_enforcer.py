"""PolicyEnforcer: deterministic first-match-wins evaluation with default deny."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from aios.governance.policies import Policy, PolicyRule


@dataclass
class EnforcementResult:
    decision: str
    policy_id: Optional[str] = None
    rule_id: Optional[str] = None
    matched: bool = False
    reason: str = "default deny (no matching rule)"

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "policy_id": self.policy_id,
            "rule_id": self.rule_id,
            "matched": self.matched,
            "reason": self.reason,
        }


class PolicyEnforcer:
    """Evaluates policies with specificity-first ordering; first match wins.

    Policies with a scope other than ``global`` are evaluated before global
    ones, so domain rules take precedence over wildcard global allows. Within
    a policy, rules run in declaration order and the first match decides.
    No match falls back to default deny.
    """

    def enforce(
        self,
        policies: list[Policy],
        action: str,
        resource: str,
        context: dict[str, Any] | None = None,
    ) -> EnforcementResult:
        ctx = dict(context or {})

        def sort_key(policy: Policy) -> tuple[int, str, str]:
            # scoped policies first (specificity 0), global policies last (1)
            specificity = 1 if policy.scope == "global" else 0
            return (specificity, policy.scope, policy.policy_id)

        for policy in sorted(policies, key=sort_key):
            if not policy.enabled:
                continue
            for rule in policy.rules:
                if rule.matches(action, resource, ctx):
                    if rule.effect == "allow":
                        return EnforcementResult(
                            decision="allow",
                            policy_id=policy.policy_id,
                            rule_id=rule.rule_id,
                            matched=True,
                            reason=f"allowed by {policy.policy_id}/{rule.rule_id}",
                        )
                    return EnforcementResult(
                        decision="deny",
                        policy_id=policy.policy_id,
                        rule_id=rule.rule_id,
                        matched=True,
                        reason=f"denied by {policy.policy_id}/{rule.rule_id}",
                    )
        return EnforcementResult(decision="deny")
