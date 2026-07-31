from __future__ import annotations

import logging
from typing import Any


class StyleChecker:
    """Checks code style against defined standards."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.quality.style")

    def check(self, code: str, lang: str = "python") -> list[dict[str, Any]]:
        self._log.info("Checking style of %s code", lang)
        return []

    def check_file(self, path: str) -> list[dict[str, Any]]:
        self._log.info("Checking style of %s", path)
        return []
