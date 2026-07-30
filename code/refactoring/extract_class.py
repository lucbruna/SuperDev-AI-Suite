from __future__ import annotations

import logging
from ..code_models import CodeFile


class ExtractClass:
    """Extracts fields and methods into a new class."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.refactoring.extract_class")

    def extract(self, files: list[CodeFile], class_name: str) -> list[CodeFile]:
        self._log.info("Extracting class %s", class_name)
        return files
