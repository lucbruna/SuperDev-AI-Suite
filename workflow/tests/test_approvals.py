from __future__ import annotations

from workflow.approvals.approval_models import Approval, ApprovalStatus
from workflow.approvals.approval_manager import ApprovalManager
from workflow.approvals.approval_policy import ApprovalPolicy
from workflow.approvals.approval_audit import ApprovalAudit


class TestApprovals:
    def test_approval_defaults(self) -> None:
        a = Approval(requester="user1")
        assert a.requester == "user1"
        assert a.status == ApprovalStatus.PENDING

    def test_approval_manager(self) -> None:
        mgr = ApprovalManager()
        a = Approval(requester="user1")
        mgr.create(a)
        assert mgr.get(a.id) == a

    def test_approval_status_update(self) -> None:
        mgr = ApprovalManager()
        a = Approval(requester="user1")
        mgr.create(a)
        mgr.update_status(a.id, ApprovalStatus.APPROVED)
        assert a.status == ApprovalStatus.APPROVED

    def test_approval_policy(self) -> None:
        policy = ApprovalPolicy(required_reviewers=2)
        a = Approval(requester="user1", reviewers=["r1", "r2"])
        assert policy.is_satisfied(a)
        a2 = Approval(requester="user1", reviewers=["r1"])
        assert not policy.is_satisfied(a2)

    def test_approval_audit(self) -> None:
        audit = ApprovalAudit()
        audit.log("submitted", "a1")
        audit.log("approved", "a1")
        history = audit.get_history("a1")
        assert len(history) == 2
