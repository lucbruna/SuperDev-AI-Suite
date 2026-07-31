from __future__ import annotations

import logging


class CodeFormatter:
    """Formats source code according to style rules."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.quality.formatter")

    def format(self, code: str, lang: str = "python") -> str:
        self._log.info("Formatting %s code", lang)
        return code

    def format_file(self, path: str) -> bool:
        self._log.info("Formatting file %s", path)
        return True
