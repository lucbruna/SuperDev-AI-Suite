from __future__ import annotations

import keyword
from typing import Any


class AutocompleteEngine:
    """Provides autocomplete suggestions from a keyword pool."""

    _POOL: dict[str, list[str]] = {
        "python": [
            "def ",
            "class ",
            "import ",
            "from ",
            "return",
            "if ",
            "else",
            "elif ",
            "for ",
            "while ",
            "try",
            "except",
            "with ",
            "async ",
            "await ",
            "self",
            "None",
            "True",
            "False",
            "print(",
            "len(",
            "range(",
            "list(",
            "dict(",
            "set(",
            "str(",
            "int(",
            "float(",
            "lambda",
            "yield",
            "raise ",
            "pass",
            "break",
            "continue",
            "global",
            "nonlocal",
            "del ",
            "assert ",
        ],
        "javascript": [
            "const ",
            "let ",
            "var ",
            "function ",
            "return",
            "if (",
            "else",
            "for (",
            "while (",
            "switch",
            "case",
            "break",
            "continue",
            "try",
            "catch",
            "throw",
            "async ",
            "await ",
            "import ",
            "export ",
            "new ",
            "null",
            "undefined",
            "true",
            "false",
            "console.log(",
            "document.",
            "window.",
            "JSON.",
        ],
        "typescript": [
            "interface ",
            "type ",
            "enum ",
            "const ",
            "let ",
            "function ",
            "return",
            "async ",
            "await ",
            "import ",
            "export ",
            "class ",
            "public ",
            "private ",
            "readonly ",
            "string",
            "number",
            "boolean",
            "any",
            "unknown",
            "never",
            "null",
            "undefined",
        ],
    }

    def __init__(self) -> None:
        self._custom: dict[str, list[str]] = {}

    def register_tokens(self, language: str, tokens: list[str]) -> None:
        self._custom.setdefault(language, []).extend(tokens)

    def suggest(self, prefix: str, language: str = "text", limit: int = 10) -> list[str]:
        pool = self._POOL.get(language, [])
        pool = pool + self._custom.get(language, [])
        if not prefix:
            return pool[:limit]
        matches = [token for token in pool if token.startswith(prefix)]
        if language == "python":
            matches = [token for token in matches if token.strip() in keyword.kwlist] + [
                token for token in matches if token.strip() not in keyword.kwlist
            ]
        return matches[:limit]

    def languages(self) -> list[str]:
        return list(self._POOL)
