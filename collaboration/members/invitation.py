"""Member invitations."""

from __future__ import annotations

import time
from typing import Any

from collaboration.collaboration_models import MemberKind, MemberRole
from collaboration.collaboration_protocols import new_id


class Invitation:
    """A pending or accepted invitation to join a workspace."""

    def __init__(self, workspace_id: str, email: str, role: MemberRole,
                 kind: MemberKind = MemberKind.HUMAN,
                 invited_by: str | None = None) -> None:
        self.invitation_id = new_id("invite")
        self.workspace_id = workspace_id
        self.email = email
        self.role = role
        self.kind = kind
        self.invited_by = invited_by
        self.status = "pending"
        self.created_at = time.time()
        self.accepted_at: float | None = None

    def accept(self) -> None:
        self.status = "accepted"
        self.accepted_at = time.time()

    def decline(self) -> None:
        self.status = "declined"

    def cancel(self) -> None:
        self.status = "cancelled"

    def to_dict(self) -> dict[str, Any]:
        return {"invitation_id": self.invitation_id,
                "workspace_id": self.workspace_id, "email": self.email,
                "role": self.role.value, "kind": self.kind.value,
                "invited_by": self.invited_by, "status": self.status,
                "created_at": self.created_at,
                "accepted_at": self.accepted_at}


class InvitationManager:
    """Lifecycle for invitations."""

    def __init__(self) -> None:
        self._invitations: dict[str, Invitation] = {}

    def create(self, workspace_id: str, email: str, role: MemberRole,
               kind: MemberKind = MemberKind.HUMAN,
               invited_by: str | None = None) -> Invitation:
        invitation = Invitation(workspace_id, email, role, kind,
                                invited_by=invited_by)
        self._invitations[invitation.invitation_id] = invitation
        return invitation

    def get(self, invitation_id: str) -> Invitation | None:
        return self._invitations.get(invitation_id)

    def accept(self, invitation_id: str) -> Invitation | None:
        invitation = self.get(invitation_id)
        if invitation is not None and invitation.status == "pending":
            invitation.accept()
        return invitation

    def decline(self, invitation_id: str) -> Invitation | None:
        invitation = self.get(invitation_id)
        if invitation is not None and invitation.status == "pending":
            invitation.decline()
        return invitation

    def cancel(self, invitation_id: str) -> Invitation | None:
        invitation = self.get(invitation_id)
        if invitation is not None and invitation.status == "pending":
            invitation.cancel()
        return invitation

    def list(self, status: str | None = None) -> list[Invitation]:
        invitations = list(self._invitations.values())
        if status is not None:
            invitations = [i for i in invitations if i.status == status]
        return invitations

    def pending_for(self, email: str) -> list[Invitation]:
        return [i for i in self._invitations.values()
                if i.email == email and i.status == "pending"]
