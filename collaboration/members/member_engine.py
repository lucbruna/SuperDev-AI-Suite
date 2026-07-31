"""Member engine: humanos e agentes de IA.

Estrutura corporativa: workspace com Owner (Diretor), Admin, Developers
(humanos) e agentes de IA (Planner, Coder, Tester, Security) como
membros de tipo AGENT.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import (MemberKind, MemberRecord,
                                                MemberRole, MemberStatus)
from collaboration.collaboration_protocols import new_id
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.members.activity import ActivityLog
from collaboration.members.availability import AvailabilityManager
from collaboration.members.invitation import InvitationManager
from collaboration.members.permissions import MemberPermissions
from collaboration.members.profile import ProfileManager


class MemberEngine:
    """Orquestrador de membros (Fase 3 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.security = security or CollaborationSecurity()
        self.registry = registry
        self.invitations = InvitationManager()
        self.profiles = ProfileManager()
        self.availability = AvailabilityManager()
        self.activity_log = ActivityLog()
        self.permissions = MemberPermissions()

    # --- members ---

    def add(self, workspace_id: str, name: str,
            role: MemberRole = MemberRole.DEVELOPER,
            kind: MemberKind = MemberKind.HUMAN,
            email: str = "", skills: list[str] | None = None,
            team_ids: list[str] | None = None,
            status: MemberStatus = MemberStatus.ACTIVE) -> MemberRecord:
        member = MemberRecord(member_id=new_id("member"),
                              workspace_id=workspace_id, name=name,
                              role=role, kind=kind, email=email,
                              skills=list(skills or []),
                              team_ids=list(team_ids or []), status=status)
        if self.registry is not None:
            self.registry.register_member(member.member_id, member)
        self.profiles.create(member.member_id, name)
        self.metrics.increment("collab.members")
        self.events.publish(CollaborationEventType.MEMBER_JOINED,
                            {"member_id": member.member_id,
                             "workspace_id": workspace_id,
                             "name": name, "role": role.value,
                             "kind": kind.value})
        return member

    def add_agent(self, workspace_id: str, name: str,
                  role: MemberRole = MemberRole.DEVELOPER,
                  skills: list[str] | None = None) -> MemberRecord:
        return self.add(workspace_id, name, role=role,
                        kind=MemberKind.AGENT, skills=skills)

    def get(self, member_id: str) -> MemberRecord | None:
        if self.registry is None:
            return None
        return self.registry.get_member(member_id)

    def remove(self, member_id: str) -> bool:
        if self.registry is not None and self.registry.remove_member(member_id):
            self.events.publish(CollaborationEventType.MEMBER_LEFT,
                                {"member_id": member_id})
            return True
        return False

    def set_status(self, member_id: str,
                   status: MemberStatus) -> MemberRecord | None:
        member = self.get(member_id)
        if member is None:
            return None
        member.status = status
        return member

    def by_workspace(self, workspace_id: str) -> list[MemberRecord]:
        if self.registry is None:
            return []
        members = []
        for member_id in self.registry.list_members():
            member = self.registry.get_member(member_id)
            if member is not None and member.workspace_id == workspace_id:
                members.append(member)
        return members

    def agents_in(self, workspace_id: str) -> list[MemberRecord]:
        return [m for m in self.by_workspace(workspace_id)
                if m.kind == MemberKind.AGENT]

    # --- invitations ---

    def invite(self, workspace_id: str, email: str,
               role: MemberRole = MemberRole.DEVELOPER,
               invited_by: str | None = None):
        return self.invitations.create(workspace_id, email, role,
                                       invited_by=invited_by)

    def accept_invite(self, invitation_id: str, name: str):
        invitation = self.invitations.accept(invitation_id)
        if invitation is None:
            return None
        member = self.add(invitation.workspace_id, name,
                          role=invitation.role, kind=invitation.kind,
                          email=invitation.email)
        return member

    # --- profile / availability / activity ---

    def update_profile(self, member_id: str, **fields: Any):
        return self.profiles.update(member_id, **fields)

    def set_available(self, member_id: str, status: str = "available") -> bool:
        return self.availability.set_status(member_id, status)

    def available_members(self) -> list[str]:
        return self.availability.available_members()

    def record_activity(self, member_id: str, action: str,
                        target: str = "") -> dict[str, Any]:
        return self.activity_log.for_member(member_id).record(action, target)

    def activity(self, member_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return self.activity_log.for_member(member_id).list(limit)

    def stats(self) -> dict[str, Any]:
        return {"members": len(self.registry.list_members())
                if self.registry else 0,
                "invitations": len(self.invitations.list()),
                "available": len(self.availability.available_members())}
