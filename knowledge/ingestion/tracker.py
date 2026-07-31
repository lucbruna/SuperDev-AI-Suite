from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import DocumentRecord, Embedding


class IngestionTracker:
    """Tracks ingestion runs and their status."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.ingestion.tracker")
        self._records: dict[str, dict[str, Any]] = {}

    def record(self, key: str, status: str, details: dict[str, Any] | None = None) -> None:
        self._records[key] = {"status": status, "details": details or {}}

    def get(self, key: str) -> dict[str, Any] | None:
        return self._records.get(key)

    def status(self, key: str) -> str | None:
        record = self._records.get(key)
        return record["status"] if record else None

    def list(self) -> list[dict[str, Any]]:
        return [{"key": key, **record} for key, record in self._records.items()]

    def stats(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self._records.values():
            counts[record["status"]] = counts.get(record["status"], 0) + 1
        return counts

    def reset(self) -> None:
        self._records.clear()
