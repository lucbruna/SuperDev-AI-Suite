from __future__ import annotations

import logging
from typing import Any


class EmbeddingMetadata:
    """Builds and validates metadata for embeddings."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.metadata")

    def build(self, document_id: str = "", source: str = "", **extra: Any) -> dict[str, Any]:
        metadata: dict[str, Any] = {"source": source}
        if document_id:
            metadata["document_id"] = document_id
        metadata.update({str(k): v for k, v in extra.items()})
        return metadata

    def validate(self, metadata: dict[str, Any]) -> bool:
        try:
            for key, value in metadata.items():
                if not isinstance(key, str):
                    return False
                if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    return False
            return True
        except (TypeError, ValueError):
            return False

    def merge(self, base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
        merged = dict(base)
        merged.update(overrides)
        return merged
