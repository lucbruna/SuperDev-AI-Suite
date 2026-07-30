from __future__ import annotations

import logging
from typing import Any


class SymbolIndex:
    """Indexes symbols by name across codebase."""

    def __init__(self) -> None:
        self._index: dict[str, list[dict[str, Any]]] = {}
        self._log = logging.getLogger("superdev.code.indexing.symbols")

    def add(self, name: str, location: dict[str, Any]) -> None:
        self._index.setdefault(name, []).append(location)

    def find(self, name: str) -> list[dict[str, Any]]:
        return self._index.get(name, [])
