"""Team management — assigns crew roles for a production."""
from __future__ import annotations

from typing import Any

ROLES = ["director", "camera", "sound", "lighting", "production", "editor"]


class TeamManagement:
    """Assigns crew based on production size."""

    def assign(self, plan: dict[str, Any], crew: int = 3) -> dict[str, Any]:
        crew = max(1, min(crew, len(ROLES)))
        members = ROLES[:crew]
        return {"count": crew, "members": members, "lead": members[0] if members else "director"}


_team_management: TeamManagement | None = None


def get_team_management() -> TeamManagement:
    global _team_management
    if _team_management is None:
        _team_management = TeamManagement()
    return _team_management
