"""Approval flow definitions."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import MemberRole

FLOWS: dict[str, list[dict[str, Any]]] = {
    "manager": [
        {"step": 1, "approver_role": MemberRole.ADMIN,
         "label": "Manager"},
    ],
    "peer": [
        {"step": 1, "approver_role": MemberRole.REVIEWER,
         "label": "Peer review"},
    ],
    "security": [
        {"step": 1, "approver_role": MemberRole.SECURITY,
         "label": "Security"},
        {"step": 2, "approver_role": MemberRole.ADMIN,
         "label": "Manager"},
    ],
    "director": [
        {"step": 1, "approver_role": MemberRole.DEVELOPER,
         "label": "Developer"},
        {"step": 2, "approver_role": MemberRole.ADMIN,
         "label": "Tech Lead"},
        {"step": 3, "approver_role": MemberRole.SECURITY,
         "label": "Security"},
        {"step": 4, "approver_role": MemberRole.OWNER,
         "label": "Diretor"},
    ],
}


class ApprovalFlow:
    """Resolves multi-step approval chains by name."""

    def steps_for(self, flow: str) -> list[dict[str, Any]]:
        steps = FLOWS.get(flow)
        if steps is None:
            return [{"step": 1, "approver_role": MemberRole.ADMIN,
                     "label": flow}]
        return [dict(step) for step in steps]

    def labels(self, flow: str) -> list[str]:
        return [step["label"] for step in self.steps_for(flow)]

    def roles(self, flow: str) -> list[MemberRole]:
        return [step["approver_role"] for step in self.steps_for(flow)]

    def all_flows(self) -> list[str]:
        return list(FLOWS)
