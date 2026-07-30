from __future__ import annotations

import logging
from typing import Any


class LanguageParser:
    """Language-specific parser dispatcher."""

    def __init__(self) -> None:
        self._parsers: dict[str, Any] = {}
        self._log = logging.getLogger("superdev.code.parsing.language")

    def register(self, language: str, parser: Any) -> None:
        self._parsers[language] = parser

    def parse(self, language: str, code: str) -> dict[str, Any]:
        parser = self._parsers.get(language)
        if parser is None:
            return {"ast": None, "errors": [f"No parser for {language}"]}
        return parser.parse(code)
