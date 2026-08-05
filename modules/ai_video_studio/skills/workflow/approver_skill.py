"""Approver skill — approval gate design for changes."""
from __future__ import annotations
from typing import Any


class ApproverSkill:
    """Design approval gates: roles, rules, and audit trail."""

    skill_id = "workflow_approver"
    skill_name = "Workflow Approver"
    skill_version = "1.0.0"
    skill_description = "Approval gate design with roles, rules, and audit."
    skill_category = "workflow"
    skill_tags = ["workflow", "approval", "governance", "gates"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        change: str,
        *,
        approvers: tuple[str, ...] = ("lead",),
        language: str = "en",
    ) -> dict[str, Any]:
        """Return an approval gate design."""
        return {
            "change": change,
            "approvers": list(approvers),
            "language": language,
            "gate": {
                "required_approvals": 1,
                "approval_mode": "any single approver",
                "escalation": "escalate after 24h idle",
                "auto_approve": "low-risk changes only",
            },
            "audit_trail": ["who", "when", "decision", "reason", "diff or payload"],
            "states": ["draft", "pending_approval", "approved", "rejected", "applied"],
            "note": f"'{change}' must not proceed until the gate is approved.",
        }
