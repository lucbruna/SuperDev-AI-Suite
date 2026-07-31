from __future__ import annotations

import logging
from typing import Any


class ProjectMembers:
    """Project membership management."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.project.members")
        self._members: dict[str, list[dict[str, Any]]] = {}

    def render(self, project_id: str) -> dict[str, Any]:
        return {"project_id": project_id, "members": self.list(project_id)}

    def list(self, project_id: str) -> list[dict[str, Any]]:
        return list(self._members.get(project_id, []))

    def add(self, project_id: str, user_id: str, role: str) -> bool:
        self._members.setdefault(project_id, []).append({"user_id": user_id, "role": role})
        return True

    def remove(self, project_id: str, user_id: str) -> bool:
        members = self._members.get(project_id, [])
        remaining = [m for m in members if m["user_id"] != user_id]
        self._members[project_id] = remaining
        return len(remaining) < len(members)
