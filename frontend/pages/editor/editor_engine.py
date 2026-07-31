from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class EditorEngine:
    """Renders the code editor page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.editor")
        self._context = context or FrontendContext()
        self._files: dict[str, dict[str, Any]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "editor",
            "open": list(self._files),
            "dirty": self.dirty_files(),
        }

    def open_file(self, path: str) -> dict[str, Any]:
        file = self._files.setdefault(path, {"content": "", "dirty": False, "opened_at": time.time()})
        return {"path": path, **file}

    def save_file(self, path: str, content: str) -> bool:
        if path not in self._files:
            self._files[path] = {"content": "", "dirty": False}
        self._files[path]["content"] = content
        self._files[path]["dirty"] = False
        return True

    def close_file(self, path: str) -> bool:
        return self._files.pop(path, None) is not None

    def dirty_files(self) -> list[str]:
        return [path for path, file in self._files.items() if file["dirty"]]
