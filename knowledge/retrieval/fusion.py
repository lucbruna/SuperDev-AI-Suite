from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import SearchResult


class Fusion:
    """Fuses ranked result lists using reciprocal rank fusion."""

    def __init__(self, constant: int = 60) -> None:
        self._log = logging.getLogger("superdev.knowledge.retrieval.fusion")
        self.constant = max(1, constant)

    def fuse(self, lists: list[list[SearchResult]]) -> list[SearchResult]:
        scores: dict[str, dict[str, Any]] = {}
        for results in lists:
            for rank, result in enumerate(results, start=1):
                entry = scores.setdefault(
                    result.text,
                    {"score": 0.0, "sources": set(), "document_id": result.document_id, "metadata": {}},
                )
                entry["score"] += 1.0 / (self.constant + rank)
                entry["sources"].add(result.source)
        ranked = sorted(scores.items(), key=lambda pair: pair[1]["score"], reverse=True)
        return [
            SearchResult(
                text=text, score=entry["score"], source="+".join(sorted(entry["sources"])),
                document_id=entry["document_id"], metadata=entry["metadata"],
            )
            for text, entry in ranked
        ]
