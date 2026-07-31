from __future__ import annotations

import logging
from typing import Any

from ...frontend_context import FrontendContext


class CodeEditorEngine:
    """Renders the code editor page with files and languages."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.code_editor")
        self._context = context or FrontendContext()
        self._files: dict[str, dict[str, Any]] = {}
        self._languages = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".json": "json",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
        }

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "code_editor",
            "open": list(self._files),
            "languages": self._languages,
        }

    def open(self, path: str) -> dict[str, Any]:
        file = self._files.setdefault(path, {"content": "", "language": self._detect(path), "dirty": False})
        return {"path": path, **file}

    def save(self, path: str, content: str) -> bool:
        file = self._files.setdefault(path, {"content": "", "language": self._detect(path), "dirty": False})
        file["content"] = content
        file["dirty"] = False
        return True

    def close(self, path: str) -> bool:
        return self._files.pop(path, None) is not None

    def _detect(self, path: str) -> str:
        for suffix, language in self._languages.items():
            if path.endswith(suffix):
                return language
        return "plaintext"
