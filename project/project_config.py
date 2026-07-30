from __future__ import annotations

from typing import Any


class ProjectConfig:
    """Configuration settings for project module."""

    def __init__(self) -> None:
        self._settings: dict[str, Any] = {
            "default_status": "draft",
            "max_team_size": 20,
            "enable_ai_planning": True,
            "auto_versioning": True,
            "storage_backend": "local",
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._settings[key] = value

    def to_dict(self) -> dict[str, Any]:
        return dict(self._settings)
