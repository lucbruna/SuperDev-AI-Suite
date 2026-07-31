from __future__ import annotations

import logging
from typing import Any


class AppearanceSettings:
    """Theme selection and preview."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.settings.appearance")
        self._themes: list[dict[str, Any]] = [
            {"theme_id": "light", "name": "Light"},
            {"theme_id": "dark", "name": "Dark"},
            {"theme_id": "system", "name": "System"},
        ]
        self._current = "system"

    def render(self) -> dict[str, Any]:
        return {"themes": self.themes(), "current": self._current, "preview": self.preview()}

    def themes(self) -> list[dict[str, Any]]:
        return list(self._themes)

    def set_theme(self, theme_id: str) -> bool:
        if theme_id not in {t["theme_id"] for t in self._themes}:
            return False
        self._current = theme_id
        return True

    def preview(self) -> dict[str, Any]:
        return {"background": "#1e1e2e" if self._current == "dark" else "#ffffff"}
