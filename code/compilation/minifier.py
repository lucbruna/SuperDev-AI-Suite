from __future__ import annotations

import logging


class Minifier:
    """Minifies source code by removing whitespace and comments."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.compilation.minifier")

    def minify(self, source: str, language: str) -> str:
        self._log.info("Minifying %s source (%d chars)", language, len(source))
        lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith(("//", "#"))]
        return "\n".join(lines)
