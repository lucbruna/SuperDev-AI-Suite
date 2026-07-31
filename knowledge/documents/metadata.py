from __future__ import annotations

import logging
from typing import Any


class DocumentMetadata:
    """Builds and validates document metadata."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.documents.metadata")

    def build(self, title: str, doc_type: str, path: str = "", author: str = "",
              tags: list[str] | None = None, **extra: Any) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "title": title,
            "doc_type": doc_type,
        }
        if path:
            metadata["path"] = path
        if author:
            metadata["author"] = author
        if tags:
            metadata["tags"] = list(tags)
        metadata.update({str(k): v for k, v in extra.items()})
        return metadata

    def tags_from_text(self, text: str, vocabulary: dict[str, bool] | None = None) -> list[str]:
        if vocabulary is None:
            vocabulary = {
                "api": True, "database": True, "frontend": True, "backend": True,
                "deploy": True, "docker": True, "security": True, "testing": True,
            }
        lowered = text.lower()
        return [tag for tag in vocabulary if tag in lowered]
