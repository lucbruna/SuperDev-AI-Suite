from __future__ import annotations

import logging
from typing import Any


class Preferences:
    """Per-user preference storage with typed getters."""

    def __init__(self, user_id: str) -> None:
        self._log = logging.getLogger("superdev.knowledge.personalization.preferences")
        self.user_id = user_id
        self._preferences: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._preferences[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._preferences.get(key, default)

    def update(self, values: dict[str, Any]) -> None:
        self._preferences.update(values)

    def all(self) -> dict[str, Any]:
        return dict(self._preferences)

    def to_dict(self) -> dict[str, Any]:
        return {"user_id": self.user_id, "preferences": dict(self._preferences)}
