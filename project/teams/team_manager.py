from __future__ import annotations

import logging
import uuid
from typing import Any


class Team:
    """Represents a project team."""

    def __init__(self, name: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.project_id = project_id
        self.members: list[str] = []
        self.roles: dict[str, str] = {}


class TeamManager:
    """Manages teams within projects."""

    def __init__(self) -> None:
        self._teams: dict[str, Team] = {}
        self._log = logging.getLogger("superdev.project.teams")

    def create(self, name: str, project_id: str) -> Team:
        team = Team(name=name, project_id=project_id)
        self._teams[team.id] = team
        self._log.info("Created team %s", team.id)
        return team

    def get(self, team_id: str) -> Team | None:
        return self._teams.get(team_id)

    def delete(self, team_id: str) -> None:
        self._teams.pop(team_id, None)

    def assign_role(self, team_id: str, user: str, role: str) -> None:
        team = self._teams.get(team_id)
        if team:
            team.roles[user] = role
            if user not in team.members:
                team.members.append(user)
