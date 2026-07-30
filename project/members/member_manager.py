from __future__ import annotations

import logging
from typing import Any


class Member:
    """Represents a project member."""

    def __init__(self, user: str, role: str = "member") -> None:
        self.user = user
        self.role = role
        self.active = True


class MemberManager:
    """Manages project member lifecycle."""

    def __init__(self) -> None:
        self._members: dict[str, dict[str, Member]] = {}
        self._log = logging.getLogger("superdev.project.members")

    def add(self, project_id: str, user: str, role: str = "member") -> None:
        self._members.setdefault(project_id, {})[user] = Member(user=user, role=role)
        self._log.info("Added %s to %s as %s", user, project_id, role)

    def remove(self, project_id: str, user: str) -> None:
        self._members.get(project_id, {}).pop(user, None)

    def get_role(self, project_id: str, user: str) -> str | None:
        member = self._members.get(project_id, {}).get(user)
        return member.role if member else None

    def list_members(self, project_id: str) -> list[Member]:
        return list(self._members.get(project_id, {}).values())
