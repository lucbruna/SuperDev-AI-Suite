from __future__ import annotations

import logging
from typing import Any


class SourceMap:
    """Maps compiled code back to source locations."""

    def __init__(self) -> None:
        self._mappings: dict[str, dict[str, Any]] = {}
        self._log = logging.getLogger("superdev.code.parsing.sourcemap")

    def add(self, source: str, compiled: str, line: int) -> None:
        self._mappings[compiled] = {"source": source, "line": line}

    def resolve(self, compiled: str) -> dict[str, Any] | None:
        return self._mappings.get(compiled)
