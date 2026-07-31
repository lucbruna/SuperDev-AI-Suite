from __future__ import annotations

import logging
from typing import Any


class DocsIndex:
    """Documentation index with search and popular docs."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.docs.index")
        self._docs: dict[str, dict[str, Any]] = {}

    def render(self) -> dict[str, Any]:
        return {"popular": self.popular(), "count": len(self._docs)}

    def search(self, query: str) -> list[dict[str, Any]]:
        return [
            {"doc_id": doc_id, **meta}
            for doc_id, meta in self._docs.items()
            if query.lower() in str(meta).lower()
        ]

    def popular(self) -> list[dict[str, Any]]:
        return sorted(self._docs.values(), key=lambda d: d.get("views", 0), reverse=True)[:5]
