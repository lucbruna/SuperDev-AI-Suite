"""Team roles and responsibilities."""

from __future__ import annotations

from collaboration.collaboration_models import MemberRole, TeamKind

ROLE_MAP = {
    TeamKind.DEVELOPMENT: [MemberRole.DEVELOPER, MemberRole.REVIEWER],
    TeamKind.QUALITY: [MemberRole.REVIEWER, MemberRole.ANALYST],
    TeamKind.SECURITY: [MemberRole.SECURITY],
    TeamKind.OPERATIONS: [MemberRole.ADMIN, MemberRole.DEVELOPER],
    TeamKind.MANAGEMENT: [MemberRole.OWNER, MemberRole.ADMIN],
    TeamKind.AGENTS: [MemberRole.DEVELOPER],
}


class TeamRoles:
    """Defines which member roles belong to each team kind."""

    def roles_for(self, kind: TeamKind) -> list[MemberRole]:
        return list(ROLE_MAP.get(kind, [MemberRole.DEVELOPER]))

    def has_role(self, kind: TeamKind, role: MemberRole) -> bool:
        return role in self.roles_for(kind)

    def role_names(self, kind: TeamKind) -> list[str]:
        return [role.value for role in self.roles_for(kind)]
