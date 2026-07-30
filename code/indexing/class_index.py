from __future__ import annotations

import logging
from typing import Any


class ClassIndex:
    """Indexes classes across the codebase."""

    def __init__(self) -> None:
        self._index: dict[str, list[dict[str, Any]]] = {}
        self._log = logging.getLogger("superdev.code.indexing.classes")

    def add(self, name: str, data: dict[str, Any]) -> None:
        self._index.setdefault(name, []).append(data)

    def find(self, name: str) -> list[dict[str, Any]]:
        return self._index.get(name, [])
