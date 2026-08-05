"""ComplianceChecker: verifies required policies are present and enforced."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aios.governance.policies import Policy


@dataclass
class ComplianceReport:
    required: list[str] = field(default_factory=list)
    satisfied: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    disabled: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing and not self.disabled

    @property
    def ratio(self) -> float:
        if not self.required:
            return 1.0
        return len(self.satisfied) / len(self.required)

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": list(self.required),
            "satisfied": list(self.satisfied),
            "missing": list(self.missing),
            "disabled": list(self.disabled),
            "ok": self.ok,
            "ratio": self.ratio,
        }


class ComplianceChecker:
    """A required policy id is satisfied only when present and enabled."""

    def evaluate(
        self, required_policies: list[str], policies: list[Policy]
    ) -> ComplianceReport:
        by_id = {policy.policy_id: policy for policy in policies}
        satisfied: list[str] = []
        missing: list[str] = []
        disabled: list[str] = []
        for policy_id in required_policies:
            policy = by_id.get(policy_id)
            if policy is None:
                missing.append(policy_id)
            elif not policy.enabled:
                disabled.append(policy_id)
            else:
                satisfied.append(policy_id)
        return ComplianceReport(
            required=sorted(required_policies),
            satisfied=sorted(satisfied),
            missing=sorted(missing),
            disabled=sorted(disabled),
        )
