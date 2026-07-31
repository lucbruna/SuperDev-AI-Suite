from __future__ import annotations

import logging
from typing import Any


class CodeEditor:
    """Editor buffer state with language detection."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.editor.code")
        self._value = ""
        self._language = "plaintext"

    def render(self) -> dict[str, Any]:
        return {"language": self._language, "length": len(self._value)}

    def set_language(self, language: str) -> None:
        self._language = language

    def get_value(self) -> str:
        return self._value

    def set_value(self, value: str) -> None:
        self._value = value
