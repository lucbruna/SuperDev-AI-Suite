from __future__ import annotations

import logging
import time
from typing import Any


class DocsEditor:
    """Markdown documentation editor."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.docs.editor")
        self._docs: dict[str, dict[str, Any]] = {}

    def render(self) -> dict[str, Any]:
        return {"open": list(self._docs)}

    def open(self, doc_id: str) -> str:
        doc = self._docs.get(doc_id)
        if doc is None:
            raise KeyError(f"unknown doc: {doc_id}")
        return doc["content"]

    def save(self, doc_id: str, content: str) -> bool:
        self._docs[doc_id] = {"content": content, "updated_at": time.time()}
        return True

    def preview(self, content: str) -> dict[str, Any]:
        lines = content.splitlines()
        return {
            "lines": len(lines),
            "words": len(content.split()),
            "headings": [l for l in lines if l.startswith("#")],
        }
