from __future__ import annotations

import logging
from typing import Any


class CodeIndexer:
    """Central indexer for codebase search."""

    def __init__(self) -> None:
        self._index: dict[str, Any] = {}
        self._log = logging.getLogger("superdev.code.indexing")

    def index(self, key: str, value: Any) -> None:
        self._index[key] = value

    def search(self, query: str) -> list[Any]:
        return [v for k, v in self._index.items() if query.lower() in k.lower()]
