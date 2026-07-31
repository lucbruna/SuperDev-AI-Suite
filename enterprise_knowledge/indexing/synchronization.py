"""Source/index synchronization diffing."""

from __future__ import annotations

from typing import Any


class IndexSynchronization:
    """Compares known index entries against crawled documents."""

    def diff(self, indexed: list[str],
             crawled: list[dict[str, Any]]) -> dict[str, Any]:
        indexed_set = set(indexed)
        crawled_ids = {doc["document_id"] for doc in crawled}
        return {
            "to_index": sorted(crawled_ids - indexed_set),
            "to_remove": sorted(indexed_set - crawled_ids),
            "synced": sorted(crawled_ids & indexed_set),
            "total": len(crawled_ids),
        }

    def needs_refresh(self, diff: dict[str, Any]) -> bool:
        return bool(diff["to_index"] or diff["to_remove"])
