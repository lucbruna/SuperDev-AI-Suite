from __future__ import annotations

from typing import Any

from ..design_system import DesignEngine


class ThemeManager:
    """Manages themes and applies them to the design engine."""

    def __init__(self, design: DesignEngine | None = None) -> None:
        self._design = design or DesignEngine()
        self._active = "light"
        self._custom: dict[str, dict[str, Any]] = {}

    @property
    def design(self) -> DesignEngine:
        return self._design

    @property
    def active(self) -> str:
        return self._active

    def apply(self, theme: str) -> str:
        if theme not in ("light", "dark") and theme not in self._custom:
            raise KeyError(f"unknown theme: {theme}")
        self._active = theme
        self._design.set_mode("dark" if theme == "dark" else "light")
        if theme in self._custom:
            self._apply_overrides(theme)
        return theme

    def register(self, name: str, overrides: dict[str, Any]) -> None:
        self._custom[name] = overrides

    def list(self) -> list[str]:
        return ["light", "dark", *self._custom.keys()]

    def _apply_overrides(self, name: str) -> None:
        tokens = self._design.tokens()
        for key, value in self._custom[name].items():
            tokens[key] = value

    def snapshot(self) -> dict[str, Any]:
        return {"active": self._active, "available": self.list(), "tokens": self._design.tokens()}
