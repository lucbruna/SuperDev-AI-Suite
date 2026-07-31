"""Team settings."""

from __future__ import annotations

from typing import Any

TEAM_DEFAULTS: dict[str, Any] = {
    "allow_agents": True,
    "require_review": True,
    "max_members": 50,
    "notifications": True,
}


class TeamSettings:
    """Per-team configuration with defaults."""

    def __init__(self, team_id: str,
                 initial: dict[str, Any] | None = None) -> None:
        self.team_id = team_id
        self._values: dict[str, Any] = dict(TEAM_DEFAULTS)
        self._values.update(initial or {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def update(self, **overrides: Any) -> None:
        self._values.update(overrides)

    def to_dict(self) -> dict[str, Any]:
        return {"team_id": self.team_id, "settings": dict(self._values)}
