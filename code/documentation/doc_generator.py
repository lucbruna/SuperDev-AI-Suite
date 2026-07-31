from __future__ import annotations

import logging
from typing import Any


class DocGenerator:
    """Extracts and writes formatted documentation from source code."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.documentation.generator")

    def from_docstrings(self, source_path: str, fmt: str = "markdown") -> str:
        raise NotImplementedError

    def from_type_hints(self, source_path: str, fmt: str = "markdown") -> str:
        raise NotImplementedError

    def from_comments(self, source_path: str, fmt: str = "markdown") -> str:
        raise NotImplementedError
