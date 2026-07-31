from __future__ import annotations

import logging
from typing import Any

from .filesystem import DesktopFilesystem
from .terminal import DesktopTerminal


class DesktopEngine:
    """Coordinates the desktop surface: platform adapters, terminal and filesystem."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.desktop")
        self._platforms: dict[str, dict[str, Any]] = {}
        self._active = "windows"
        self.terminal = DesktopTerminal()
        self.filesystem = DesktopFilesystem()

    def register_platform(self, name: str, config: dict[str, Any]) -> None:
        self._platforms[name] = {"name": name, **config}

    def set_active(self, name: str) -> bool:
        if name not in self._platforms:
            return False
        self._active = name
        return True

    def active(self) -> str:
        return self._active

    def platforms(self) -> list[str]:
        return list(self._platforms)

    def render(self) -> dict[str, Any]:
        return {
            "surface": "desktop",
            "active": self._active,
            "platforms": self.platforms(),
            "terminal": self.terminal.status(),
            "filesystem": self.filesystem.status(),
        }
