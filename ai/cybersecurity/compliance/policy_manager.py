"""
Policy Management
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PolicyStatus(Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    RETIRED = "retired"
    UNDER_REVIEW = "under_review"


@dataclass
class Policy:
    policy_id: str
    name: str
    description: str = ""
    status: PolicyStatus = PolicyStatus.DRAFT
    version: str = "1.0"
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    effective_date: datetime | None = None
    review_date: datetime | None = None
    rules: list[dict[str, Any]] = field(default_factory=list)
    exceptions: list[dict[str, str]] = field(default_factory=list)


@dataclass
class PolicyException:
    exception_id: str
    policy_id: str
    reason: str = ""
    approved_by: str = ""
    expires_at: datetime | None = None


class PolicyManager:
    def __init__(self):
        self.policies: dict[str, Policy] = {}
        self.exceptions: dict[str, PolicyException] = {}

    def create_policy(self, policy_id: str, name: str, description: str = "", owner: str = "") -> Policy:
        policy = Policy(policy_id=policy_id, name=name, description=description, owner=owner)
        self.policies[policy_id] = policy
        return policy

    def update_policy(self, policy_id: str, **kwargs) -> bool:
        policy = self.policies.get(policy_id)
        if policy:
            for k, v in kwargs.items():
                if hasattr(policy, k):
                    setattr(policy, k, v)
            policy.updated_at = datetime.now()
            return True
        return False

    def activate_policy(self, policy_id: str) -> bool:
        policy = self.policies.get(policy_id)
        if policy:
            policy.status = PolicyStatus.ACTIVE
            policy.effective_date = datetime.now()
            return True
        return False

    def retire_policy(self, policy_id: str) -> bool:
        policy = self.policies.get(policy_id)
        if policy:
            policy.status = PolicyStatus.RETIRED
            return True
        return False

    def add_exception(self, policy_id: str, reason: str, approved_by: str = "") -> PolicyException:
        exc_id = f"exc_{len(self.exceptions)}"
        exc = PolicyException(exception_id=exc_id, policy_id=policy_id, reason=reason, approved_by=approved_by)
        self.exceptions[exc_id] = exc
        return exc

    def get_active_policies(self) -> list[Policy]:
        return [p for p in self.policies.values() if p.status == PolicyStatus.ACTIVE]

    def get_policy(self, policy_id: str) -> Policy | None:
        return self.policies.get(policy_id)

    def get_exceptions(self, policy_id: str) -> list[PolicyException]:
        return [e for e in self.exceptions.values() if e.policy_id == policy_id]

    def count(self) -> int:
        return len(self.policies)
