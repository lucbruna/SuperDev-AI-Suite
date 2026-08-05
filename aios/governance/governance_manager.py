"""GovernanceManager: facade combining policies, enforcement, audit and approvals."""
from __future__ import annotations

from typing import Any, Optional

from aios.governance.approval_workflow import ApprovalWorkflow
from aios.governance.audit_trail import AuditTrail
from aios.governance.compliance_checker import ComplianceChecker, ComplianceReport
from aios.governance.policies import Policy
from aios.governance.policy_enforcer import EnforcementResult, PolicyEnforcer


class GovernanceManager:
    """Enforces policies, records every decision, and checks compliance."""

    def __init__(
        self,
        policies: list[Policy] | None = None,
        enforcer: PolicyEnforcer | None = None,
        audit: AuditTrail | None = None,
        compliance: ComplianceChecker | None = None,
        approvals: ApprovalWorkflow | None = None,
    ) -> None:
        self._policies: dict[str, Policy] = {
            policy.policy_id: policy for policy in (policies or [])
        }
        self.enforcer = enforcer if enforcer is not None else PolicyEnforcer()
        self.audit = audit if audit is not None else AuditTrail()
        self.compliance = compliance if compliance is not None else ComplianceChecker()
        self.approvals = approvals if approvals is not None else ApprovalWorkflow()

    def add_policy(self, policy: Policy) -> bool:
        if policy.policy_id in self._policies:
            raise KeyError(f"policy {policy.policy_id!r} already registered")
        self._policies[policy.policy_id] = policy
        return True

    def remove_policy(self, policy_id: str) -> bool:
        return self._policies.pop(policy_id, None) is not None

    def enable(self, policy_id: str) -> bool:
        policy = self._policies.get(policy_id)
        if policy is None:
            return False
        policy.enabled = True
        return True

    def disable(self, policy_id: str) -> bool:
        policy = self._policies.get(policy_id)
        if policy is None:
            return False
        policy.enabled = False
        return True

    def policies(self) -> list[Policy]:
        return [self._policies[key] for key in sorted(self._policies)]

    def enforce(
        self,
        subject: str,
        action: str,
        resource: str,
        context: dict[str, Any] | None = None,
    ) -> EnforcementResult:
        result = self.enforcer.enforce(self.policies(), action, resource, context)
        self.audit.record(
            subject=subject,
            action=action,
            resource=resource,
            decision=result.decision,
            detail=result.reason,
        )
        return result

    def check_compliance(self, required_policies: list[str]) -> ComplianceReport:
        return self.compliance.evaluate(required_policies, self.policies())

    def snapshot(self) -> dict[str, Any]:
        return {
            "policies": [policy.to_dict() for policy in self.policies()],
            "audit": self.audit.summary(),
            "approvals": self.approvals.summary(),
        }
