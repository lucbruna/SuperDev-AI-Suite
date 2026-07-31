"""Source crawler for knowledge indexing."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_protocols import new_id


class KnowledgeCrawler:
    """Visits configured sources and yields text documents to index."""

    def __init__(self) -> None:
        self._sources: dict[str, list[dict[str, Any]]] = {}

    def add_source(self, source_id: str,
                   documents: list[dict[str, Any]] | None = None) -> None:
        self._sources.setdefault(source_id, [])
        if documents:
            self._sources[source_id].extend(documents)

    def crawl(self, source_id: str = "") -> list[dict[str, Any]]:
        visited: list[dict[str, Any]] = []
        targets = [source_id] if source_id else list(self._sources)
        for sid in targets:
            for index, document in enumerate(self._sources.get(sid, [])):
                document_id = document.get("document_id") or new_id("doc")
                visited.append({"source_id": sid, "document_id": document_id,
                                "title": document.get("title", ""),
                                "content": document.get("content", ""),
                                "tags": list(document.get("tags", []))})
        return visited

    def source_count(self) -> int:
        return len(self._sources)

    def sources(self) -> list[str]:
        return list(self._sources)
