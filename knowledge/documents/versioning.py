from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any


class DocumentVersioning:
    """Tracks document versions and history."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.versioning")
        self._history: dict[str, list[dict[str, Any]]] = {}

    def snapshot(self, document_id: str, content: str, version: int,
                 author: str = "system") -> None:
        self._history.setdefault(document_id, []).append(
            {
                "version": version,
                "content": content,
                "author": author,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def history(self, document_id: str) -> list[dict[str, Any]]:
        return list(self._history.get(document_id, []))

    def previous(self, document_id: str, current_version: int) -> dict[str, Any] | None:
        entries = [e for e in self._history.get(document_id, []) if e["version"] < current_version]
        return entries[-1] if entries else None

    def count(self, document_id: str) -> int:
        return len(self._history.get(document_id, []))
