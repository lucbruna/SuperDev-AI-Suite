from __future__ import annotations

import logging
from typing import Any


class SemanticIndex:
    """Indexes code by semantic meaning."""

    def __init__(self) -> None:
        self._index: dict[str, list[str]] = {}
        self._log = logging.getLogger("superdev.code.indexing.semantic")

    def add(self, concept: str, code: str) -> None:
        self._index.setdefault(concept, []).append(code)

    def search(self, concept: str) -> list[str]:
        return self._index.get(concept, [])
