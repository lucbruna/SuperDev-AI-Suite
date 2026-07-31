"""Team structure: teams, roles and member composition."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import TeamKind, TeamRecord
from collaboration.collaboration_protocols import new_id
from collaboration.teams.team_roles import TeamRoles


class TeamStructure:
    """Builds and inspects team structures (ex: Projeto ERP com equipe
    Desenvolvimento + Qualidade + Agentes IA)."""

    def __init__(self) -> None:
        self.roles = TeamRoles()
        self._teams: dict[str, TeamRecord] = {}

    def add_team(self, workspace_id: str, name: str,
                 kind: TeamKind = TeamKind.DEVELOPMENT,
                 lead_id: str | None = None) -> TeamRecord:
        team = TeamRecord(team_id=new_id("team"), workspace_id=workspace_id,
                          name=name, kind=kind, lead_id=lead_id)
        self._teams[team.team_id] = team
        return team

    def get(self, team_id: str) -> TeamRecord | None:
        return self._teams.get(team_id)

    def list(self) -> list[str]:
        return list(self._teams)

    def remove(self, team_id: str) -> bool:
        return self._teams.pop(team_id, None) is not None

    def by_kind(self, kind: TeamKind) -> list[TeamRecord]:
        return [team for team in self._teams.values() if team.kind == kind]

    def summary(self, team_id: str) -> dict[str, Any]:
        team = self._teams.get(team_id)
        if team is None:
            raise KeyError(f"unknown team: {team_id}")
        return {"team_id": team.team_id, "name": team.name,
                "kind": team.kind.value, "lead_id": team.lead_id,
                "roles": self.roles.role_names(team.kind)}
