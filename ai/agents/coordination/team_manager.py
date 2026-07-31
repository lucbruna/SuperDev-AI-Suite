from __future__ import annotations

from typing import Any


class TeamManager:
    """Manages agent teams."""

    def __init__(self) -> None:
        self._teams: dict[str, list[str]] = {}

    @property
    def team_count(self) -> int:
        return len(self._teams)

    def create_team(self, team_id: str) -> None:
        if team_id not in self._teams:
            self._teams[team_id] = []

    def add_member(self, team_id: str, agent_id: str) -> bool:
        if team_id in self._teams and agent_id not in self._teams[team_id]:
            self._teams[team_id].append(agent_id)
            return True
        return False

    def remove_member(self, team_id: str, agent_id: str) -> bool:
        if team_id in self._teams and agent_id in self._teams[team_id]:
            self._teams[team_id].remove(agent_id)
            return True
        return False

    def get_team(self, team_id: str) -> list[str]:
        return list(self._teams.get(team_id, []))

    def delete_team(self, team_id: str) -> bool:
        return self._teams.pop(team_id, None) is not None

    def list_teams(self) -> list[str]:
        return list(self._teams.keys())

    def to_dict(self) -> dict[str, Any]:
        return {"teams": {t: list(m) for t, m in self._teams.items()}}
