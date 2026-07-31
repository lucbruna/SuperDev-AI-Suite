from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import DocumentRecord


class BatchProcessor:
    """Processes documents in batches, tracking per-item outcomes."""

    def __init__(self, batch_size: int = 10) -> None:
        self._log = logging.getLogger("superdev.knowledge.ingestion.batch_processor")
        self.batch_size = max(1, batch_size)

    def split(self, documents: list[DocumentRecord]) -> list[list[DocumentRecord]]:
        return [
            documents[index:index + self.batch_size]
            for index in range(0, len(documents), self.batch_size)
        ]

    def process(self, documents: list[DocumentRecord], processor: Any) -> dict[str, Any]:
        succeeded = 0
        failed = 0
        results: list[dict[str, Any]] = []
        for batch in self.split(documents):
            for document in batch:
                try:
                    result = processor(document)
                    succeeded += 1
                    results.append({"document_id": result, "status": "ok"})
                except Exception as exc:  # noqa: BLE001 - batch processor surfaces per-item failures
                    failed += 1
                    self._log.warning("failed to ingest %s: %s", getattr(document, "title", "?"), exc)
                    results.append({"document_id": getattr(document, "id", ""), "status": "failed", "error": str(exc)})
        return {
            "total": len(documents),
            "succeeded": succeeded,
            "failed": failed,
            "results": results,
        }
