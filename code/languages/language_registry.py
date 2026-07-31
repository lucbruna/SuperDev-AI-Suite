from __future__ import annotations

import logging
from typing import Any


class LanguageRegistry:
    """Registry of supported programming languages."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.languages")
        self._languages: dict[str, dict[str, Any]] = {}

    def register(self, name: str, config: dict[str, Any]) -> None:
        self._languages[name] = config
        self._log.info("Registered language: %s", name)

    def get(self, name: str) -> dict[str, Any] | None:
        return self._languages.get(name)

    def list_languages(self) -> list[str]:
        return list(self._languages.keys())

    def detect(self, filename: str) -> str | None:
        ext_map = {
            ".py": "python", ".js": "javascript", ".ts": "typescript",
            ".java": "java", ".go": "go", ".rs": "rust",
            ".cpp": "cpp", ".cs": "csharp", ".php": "php",
            ".rb": "ruby", ".swift": "swift", ".kt": "kotlin",
            ".scala": "scala", ".lua": "lua", ".r": "r",
        }
        import os
        ext = os.path.splitext(filename)[1].lower()
        return ext_map.get(ext)
