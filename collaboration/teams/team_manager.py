"""Team lifecycle management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import TeamKind, TeamRecord
from collaboration.collaboration_protocols import new_id
from collaboration.teams.team_activity import TeamActivity
from collaboration.teams.team_settings import TeamSettings
from collaboration.teams.team_structure import TeamStructure


class TeamManager:
    """CRUD and composition for teams."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry
        self.structure = TeamStructure()
        self._settings: dict[str, TeamSettings] = {}
        self._activity: dict[str, TeamActivity] = {}

    def create(self, workspace_id: str, name: str,
               kind: TeamKind = TeamKind.DEVELOPMENT,
               lead_id: str | None = None) -> TeamRecord:
        team = self.structure.add_team(workspace_id, name, kind,
                                       lead_id=lead_id)
        if self.registry is not None:
            self.registry.register_team(team.team_id, team)
        self._settings[team.team_id] = TeamSettings(team.team_id)
        self._activity[team.team_id] = TeamActivity(team.team_id)
        return team

    def get(self, team_id: str) -> TeamRecord | None:
        return self.structure.get(team_id)

    def list(self) -> list[str]:
        return self.structure.list()

    def remove(self, team_id: str) -> bool:
        removed = self.structure.remove(team_id)
        self._settings.pop(team_id, None)
        self._activity.pop(team_id, None)
        if removed and self.registry is not None:
            self.registry.remove_team(team_id)
        return removed

    def settings(self, team_id: str) -> TeamSettings:
        settings = self._settings.get(team_id)
        if settings is None:
            raise KeyError(f"unknown team: {team_id}")
        return settings

    def activity(self, team_id: str) -> TeamActivity:
        activity = self._activity.get(team_id)
        if activity is None:
            raise KeyError(f"unknown team: {team_id}")
        return activity

    def update_settings(self, team_id: str,
                        **overrides: Any) -> TeamSettings:
        settings = self.settings(team_id)
        settings.update(**overrides)
        return settings

    def set_lead(self, team_id: str, lead_id: str) -> TeamRecord | None:
        team = self.get(team_id)
        if team is None:
            return None
        team.lead_id = lead_id
        return team

    def count(self) -> int:
        return self.structure.list().__len__()
