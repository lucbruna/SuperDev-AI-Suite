"""Workspace permissions by member role."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import MemberRole
from collaboration.collaboration_security import CollaborationSecurity

ALLOWED_ACTIONS = {
    "manage_workspace": [MemberRole.OWNER, MemberRole.ADMIN],
    "create_team": [MemberRole.OWNER, MemberRole.ADMIN],
    "create_project": [MemberRole.OWNER, MemberRole.ADMIN],
    "create_task": [MemberRole.OWNER, MemberRole.ADMIN,
                    MemberRole.DEVELOPER, MemberRole.REVIEWER,
                    MemberRole.SECURITY, MemberRole.ANALYST],
    "review": [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.REVIEWER,
               MemberRole.SECURITY],
    "approve": [MemberRole.OWNER, MemberRole.ADMIN],
    "deploy": [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.SECURITY],
    "view": list(MemberRole),
}


class WorkspacePermissions:
    """Role-based access checks within a workspace."""

    def __init__(self, workspace_id: str,
                 security: CollaborationSecurity | None = None) -> None:
        self.workspace_id = workspace_id
        self.security = security or CollaborationSecurity()

    def can(self, role: MemberRole, action: str) -> bool:
        if action not in ALLOWED_ACTIONS:
            return False
        return role in ALLOWED_ACTIONS[action]

    def require(self, role: MemberRole, action: str) -> bool:
        allowed = self.can(role, action)
        if not allowed:
            self.security.audit(role.value, f"deny:{action}", self.workspace_id)
        return allowed

    def allowed_actions(self, role: MemberRole) -> list[str]:
        return [action for action, roles in ALLOWED_ACTIONS.items()
                if role in roles]

    def report(self) -> dict[str, Any]:
        return {"workspace_id": self.workspace_id,
                "actions": {r.value: self.allowed_actions(r)
                            for r in MemberRole}}
