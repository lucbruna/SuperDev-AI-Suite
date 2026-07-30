from __future__ import annotations

import logging
from typing import Any


class SymbolIndex:
    """Indexes symbols across the codebase."""

    def __init__(self) -> None:
        self._symbols: dict[str, list[dict[str, Any]]] = {}
        self._log = logging.getLogger("superdev.code.understanding.symbols")

    def add(self, name: str, location: dict[str, Any]) -> None:
        self._symbols.setdefault(name, []).append(location)

    def find(self, name: str) -> list[dict[str, Any]]:
        return self._symbols.get(name, [])
