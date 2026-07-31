from __future__ import annotations

import logging
from typing import Any


class DocumentationEngine:
    """Central documentation engine for code documentation generation."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.documentation")

    def generate(self, source_path: str, output_dir: str, fmt: str = "markdown") -> None:
        raise NotImplementedError

    def validate(self, source_path: str) -> list[str]:
        raise NotImplementedError

    def export(self, source_path: str, fmt: str = "html") -> str:
        raise NotImplementedError
