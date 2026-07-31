from __future__ import annotations

import logging


class DocValidator:
    """Validates documentation completeness, correctness, and style."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.documentation.validator")

    def validate_docstrings(self, source_path: str) -> list[str]:
        raise NotImplementedError

    def validate_coverage(self, source_path: str, min_coverage: float = 0.8) -> list[str]:
        raise NotImplementedError

    def validate_links(self, docs_path: str) -> list[str]:
        raise NotImplementedError
