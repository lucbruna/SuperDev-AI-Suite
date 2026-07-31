from __future__ import annotations

import logging
from typing import Any


class EditorTabs:
    """Open file tabs in the editor."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.editor.tabs")
        self._tabs: list[str] = []
        self._active: str | None = None

    def render(self) -> dict[str, Any]:
        return {"tabs": list(self._tabs), "active": self._active}

    def open(self, path: str) -> None:
        if path not in self._tabs:
            self._tabs.append(path)
        self._active = path

    def close(self, path: str) -> None:
        if path in self._tabs:
            self._tabs.remove(path)
        if self._active == path:
            self._active = self._tabs[-1] if self._tabs else None

    def active(self) -> str | None:
        return self._active

    def set_active(self, path: str) -> None:
        if path not in self._tabs:
            raise KeyError(f"tab not open: {path}")
        self._active = path
