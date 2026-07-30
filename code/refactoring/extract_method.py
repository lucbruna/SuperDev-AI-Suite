from __future__ import annotations

import logging
from ..code_models import CodeFile


class ExtractMethod:
    """Extracts code blocks into separate methods."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.refactoring.extract_method")

    def extract(self, file: CodeFile, start: int, end: int, name: str) -> list[CodeFile]:
        self._log.info("Extracting method %s from %s", name, file.path)
        return [file]
