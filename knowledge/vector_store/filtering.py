from __future__ import annotations

import logging
from typing import Any


class Filtering:
    """Filters search results by metadata and fields."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.vector_store.filtering")

    def apply(self, results: list[Any], metadata_eq: dict[str, Any] | None = None,
              source: str | None = None, document_id: str | None = None) -> list[Any]:
        filtered = results
        if metadata_eq:
            filtered = [r for r in filtered if all(r.metadata.get(k) == v for k, v in metadata_eq.items())]
        if source is not None:
            filtered = [r for r in filtered if r.source == source]
        if document_id is not None:
            filtered = [r for r in filtered if r.document_id == document_id]
        return filtered

    def apply_score(self, results: list[Any], min_score: float) -> list[Any]:
        return [r for r in results if r.score >= min_score]
