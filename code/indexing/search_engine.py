from __future__ import annotations

import logging
from typing import Any


class SearchEngine:
    """Full-text and semantic search over indexed code."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.indexing.search")

    def search(self, query: str, index: dict[str, Any]) -> list[str]:
        return [k for k in index if query.lower() in k.lower()]
