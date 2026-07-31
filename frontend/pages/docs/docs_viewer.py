from __future__ import annotations

import logging
import re
from typing import Any


class DocsViewer:
    """Renders documentation content with an outline."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.docs.viewer")
        self._docs: dict[str, dict[str, Any]] = {}

    def render(self, doc_id: str) -> dict[str, Any]:
        return {
            "doc_id": doc_id,
            "content": self.content(doc_id),
            "headings": self.headings(doc_id),
        }

    def content(self, doc_id: str) -> str:
        doc = self._docs.get(doc_id)
        if doc is None:
            raise KeyError(f"unknown doc: {doc_id}")
        return doc.get("content", "")

    def headings(self, doc_id: str) -> list[dict[str, Any]]:
        content = self.content(doc_id)
        headings: list[dict[str, Any]] = []
        for line in content.splitlines():
            match = re.match(r"^(#{1,6})\s+(.*)$", line)
            if match:
                headings.append({"level": len(match.group(1)), "title": match.group(2)})
        return headings
