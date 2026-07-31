"""Member permissions."""

from __future__ import annotations

from collaboration.collaboration_models import MemberKind, MemberRole


class MemberPermissions:
    """Permission checks for workspace members."""

    def __init__(self) -> None:
        self._role_rank = {
            MemberRole.OWNER: 5,
            MemberRole.ADMIN: 4,
            MemberRole.SECURITY: 3,
            MemberRole.REVIEWER: 2,
            MemberRole.ANALYST: 2,
            MemberRole.DEVELOPER: 1,
        }

    def rank(self, role: MemberRole) -> int:
        return self._role_rank.get(role, 0)

    def can(self, role: MemberRole, minimum: MemberRole) -> bool:
        return self.rank(role) >= self.rank(minimum)

    def can_manage(self, role: MemberRole) -> bool:
        return self.can(role, MemberRole.ADMIN)

    def can_review(self, role: MemberRole) -> bool:
        return self.can(role, MemberRole.REVIEWER)

    def agents_only(self, kind: MemberKind) -> bool:
        return kind == MemberKind.AGENT

    def describe(self, role: MemberRole) -> dict:
        return {"role": role.value, "rank": self.rank(role),
                "manage": self.can_manage(role),
                "review": self.can_review(role)}
