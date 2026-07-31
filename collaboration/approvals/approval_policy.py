"""Approval policies."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import (EntityKind, MemberKind,
                                                MemberRole, MemberStatus)


class ApprovalPolicy:
    """Rules that decide who may approve a request."""

    def __init__(self) -> None:
        self._requirements: dict[str, MemberRole] = {}

    def require_role(self, target_kind: EntityKind,
                     role: MemberRole) -> None:
        self._requirements[target_kind.value] = role

    def required_role(self, target_kind: EntityKind) -> MemberRole:
        return self._requirements.get(
            target_kind.value, MemberRole.ADMIN)

    def can_approve(self, member: Any, target_kind: EntityKind) -> bool:
        if member is None:
            return False
        if member.kind == MemberKind.AGENT:
            return False
        if getattr(member, "status", MemberStatus.ACTIVE) != \
                MemberStatus.ACTIVE:
            return False
        return member.role in (MemberRole.OWNER, MemberRole.ADMIN,
                               self.required_role(target_kind))

    def can_request(self, member: Any) -> bool:
        if member is None:
            return False
        return member.kind == MemberKind.HUMAN and \
            member.status == MemberStatus.ACTIVE

    def describe(self) -> dict[str, Any]:
        return {kind: role.value
                for kind, role in self._requirements.items()}
