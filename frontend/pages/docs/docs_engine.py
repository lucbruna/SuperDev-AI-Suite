from __future__ import annotations

import logging
from typing import Any

from ...frontend_context import FrontendContext


class DocsEngine:
    """Renders the documentation page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.docs")
        self._context = context or FrontendContext()
        self._docs: dict[str, dict[str, Any]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "docs",
            "count": len(self._docs),
            "tree": self.tree(),
        }

    def tree(self) -> dict[str, Any]:
        tree: dict[str, Any] = {}
        for doc_id, meta in self._docs.items():
            parts = doc_id.split("/")
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = meta.get("title", doc_id)
        return tree

    def open(self, doc_id: str) -> dict[str, Any]:
        doc = self._docs.get(doc_id)
        if doc is None:
            raise KeyError(f"unknown doc: {doc_id}")
        return {"doc_id": doc_id, **doc}

    def search(self, query: str) -> list[dict[str, Any]]:
        return [
            {"doc_id": doc_id, **meta}
            for doc_id, meta in self._docs.items()
            if query.lower() in str(meta).lower()
        ]
