from __future__ import annotations

import keyword
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Token:
    """A single syntax token."""

    kind: str  # keyword | string | number | comment | identifier | operator
    value: str
    start: int
    end: int


class SyntaxHighlighter:
    """Lightweight regex-based syntax highlighter."""

    EXTENSION_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".jsx": "jsx",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".html": "html",
        ".css": "css",
        ".sql": "sql",
        ".sh": "shell",
    }

    _PATTERNS: dict[str, list[tuple[str, str]]] = {
        "python": [
            (r"#[^\n]*", "comment"),
            (r"\"\"\"[\s\S]*?\"\"\"|'''[\s\S]*?'''", "string"),
            (r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", "string"),
            (r"\b\d+(?:\.\d+)?\b", "number"),
        ],
        "default": [
            (r"//[^\n]*|#[^\n]*|<!--[\s\S]*?-->", "comment"),
            (r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`", "string"),
            (r"\b\d+(?:\.\d+)?\b", "number"),
        ],
    }

    _KEYWORDS = set(keyword.kwlist)

    def language_for_path(self, path: str) -> str:
        lower = path.lower()
        for ext, language in self.EXTENSION_MAP.items():
            if lower.endswith(ext):
                return language
        return "text"

    def tokenize(self, code: str, language: str = "python") -> list[dict[str, Any]]:
        tokens: list[dict[str, Any]] = []
        patterns = self._PATTERNS.get(language, self._PATTERNS["default"])
        combined = "|".join(f"({pattern})" for pattern, _ in patterns)
        regex = re.compile(combined)
        pos = 0
        for match in regex.finditer(code):
            if match.start() > pos:
                self._emit_plain(tokens, code[pos : match.start()], pos, language)
            for index, (_, kind) in enumerate(patterns):
                if match.group(index + 1) is not None:
                    tokens.append(
                        {"kind": kind, "value": match.group(0), "start": match.start(), "end": match.end()}
                    )
                    break
            pos = match.end()
        if pos < len(code):
            self._emit_plain(tokens, code[pos:], pos, language)
        return tokens

    def _emit_plain(self, tokens: list[dict[str, Any]], text: str, start: int, language: str) -> None:
        word_pattern = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
        pos = start
        for match in word_pattern.finditer(text):
            if match.start() > pos - start:
                tokens.append(
                    {
                        "kind": "operator",
                        "value": text[pos - start : match.start()],
                        "start": pos,
                        "end": match.start() + start - start + pos - start,
                    }
                )
            value = match.group(0)
            kind = "keyword" if value in self._KEYWORDS else "identifier"
            tokens.append({"kind": kind, "value": value, "start": start + match.start(), "end": start + match.end()})
            pos = start + match.end()
        if pos < start + len(text):
            tokens.append({"kind": "operator", "value": text[pos - start :], "start": pos, "end": start + len(text)})
