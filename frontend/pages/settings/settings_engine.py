from __future__ import annotations

import logging
from typing import Any

from ...frontend_context import FrontendContext


class SettingsEngine:
    """Renders the settings page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.settings")
        self._context = context or FrontendContext()
        self._values: dict[str, Any] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "settings",
            "sections": self.sections(),
            "values": dict(self._values),
        }

    def sections(self) -> list[dict[str, Any]]:
        return [
            {"id": "general", "name": "General"},
            {"id": "appearance", "name": "Appearance"},
            {"id": "notifications", "name": "Notifications"},
            {"id": "storage", "name": "Storage"},
            {"id": "integrations", "name": "Integrations"},
            {"id": "privacy", "name": "Privacy"},
            {"id": "advanced", "name": "Advanced"},
        ]

    def get(self, key: str) -> Any:
        return self._values.get(key)

    def set(self, key: str, value: Any) -> bool:
        self._values[key] = value
        return True

    def reset(self) -> bool:
        self._values.clear()
        return True
