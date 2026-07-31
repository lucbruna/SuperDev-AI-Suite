from __future__ import annotations

import logging
from typing import Any


class DocsSearch:
    """Full-text search across the documentation."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.docs.search")
        self._docs: list[dict[str, Any]] = []

    def render(self) -> dict[str, Any]:
        return {"indexed": len(self._docs)}

    def query(self, text: str) -> list[dict[str, Any]]:
        return [doc for doc in self._docs if text.lower() in str(doc).lower()]

    def filter(self, results: list[dict[str, Any]], tag: str) -> list[dict[str, Any]]:
        return [r for r in results if tag in r.get("tags", [])]
