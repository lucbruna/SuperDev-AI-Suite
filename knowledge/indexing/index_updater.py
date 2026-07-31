from __future__ import annotations

import logging
from typing import Any

from .index_manager import IndexManager


class IndexUpdater:
    """Applies incremental additions and removals to the index family."""

    def __init__(self, index_manager: IndexManager | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.indexing.index_updater")
        self.index_manager = index_manager or IndexManager()

    def add(self, document_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        self.index_manager.add(document_id, text, metadata)

    def update(self, document_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        self.index_manager.remove(document_id)
        self.index_manager.add(document_id, text, metadata)

    def remove(self, document_id: str) -> None:
        self.index_manager.remove(document_id)

    def keyword_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        hits = self.index_manager.keyword.search(query)
        return [
            {
                "document_id": document_id,
                "score": score,
                "metadata": self.index_manager.metadata.get(document_id),
            }
            for document_id, score in hits[:top_k]
        ]
