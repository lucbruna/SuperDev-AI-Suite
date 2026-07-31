from __future__ import annotations

import logging
from typing import Any


class SemanticIndex:
    """Builds semantic understanding of code."""

    def __init__(self) -> None:
        self._index: dict[str, dict[str, Any]] = {}
        self._log = logging.getLogger("superdev.code.understanding.semantic")

    def index(self, key: str, data: dict[str, Any]) -> None:
        self._index[key] = data

    def search(self, _query: str) -> list[dict[str, Any]]:
        return []
