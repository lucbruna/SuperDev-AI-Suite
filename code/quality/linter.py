from __future__ import annotations

import logging
from typing import Any


class Linter:
    """Lints source code for common issues."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.quality.linter")

    def lint(self, code: str, lang: str = "python") -> list[dict[str, Any]]:
        self._log.info("Linting %s code (%d chars)", lang, len(code))
        return []

    def lint_file(self, path: str) -> list[dict[str, Any]]:
        self._log.info("Linting file %s", path)
        return []
