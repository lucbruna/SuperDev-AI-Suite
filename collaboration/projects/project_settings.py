"""Project settings."""

from __future__ import annotations

from typing import Any

PROJECT_DEFAULTS: dict[str, Any] = {
    "allow_agents": True,
    "require_approval": True,
    "progress_autoupdate": True,
    "notifications": True,
}


class ProjectSettings:
    """Per-project configuration with defaults."""

    def __init__(self, project_id: str,
                 initial: dict[str, Any] | None = None) -> None:
        self.project_id = project_id
        self._values: dict[str, Any] = dict(PROJECT_DEFAULTS)
        self._values.update(initial or {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def update(self, **overrides: Any) -> None:
        self._values.update(overrides)

    def to_dict(self) -> dict[str, Any]:
        return {"project_id": self.project_id,
                "settings": dict(self._values)}
