from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from ..knowledge_interfaces import MemoryStore
from ..knowledge_models import MemoryRecord


class MemoryOptimizer:
    """Consolidates and deduplicates memory records to keep knowledge lean."""

    def __init__(self, store: MemoryStore) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.optimizer")
        self._store = store

    def deduplicate(self) -> int:
        removed = 0
        seen: dict[str, str] = {}
        for record_id, record in self._snapshot_ids():
            key = record.content.strip().lower()
            existing = seen.get(key)
            if existing is not None:
                if self._store.delete(record_id):
                    removed += 1
            else:
                seen[key] = record_id
        return removed

    def consolidate_similar(self, threshold: float = 0.8) -> int:
        records = self._store.list()
        merged = 0
        for i, left in enumerate(records):
            for right in records[i + 1:]:
                if self._similarity(left.content, right.content) >= threshold:
                    left.importance = max(left.importance, right.importance)
                    left.access_count += right.access_count
                    merged += 1
        return merged

    def reweight(self) -> int:
        """Boost frequently accessed memories and decay stale ones."""
        adjusted = 0
        for record in self._store.list():
            boost = min(record.access_count * 0.05, 0.3)
            new_importance = min(1.0, record.importance + boost)
            if abs(new_importance - record.importance) > 1e-6:
                record.importance = new_importance
                adjusted += 1
        return adjusted

    def top_keywords(self, limit: int = 20) -> list[tuple[str, int]]:
        words: Counter[str] = Counter()
        for record in self._store.list():
            for token in record.content.split():
                cleaned = token.strip(".,;:!?()[]{}'\"")
                if len(cleaned) > 3 and cleaned.isalpha():
                    words[cleaned.lower()] += 1
        return words.most_common(limit)

    @staticmethod
    def _similarity(left: str, right: str) -> float:
        left_tokens = set(left.lower().split())
        right_tokens = set(right.lower().split())
        if not left_tokens or not right_tokens:
            return 0.0
        overlap = len(left_tokens & right_tokens)
        return overlap / min(len(left_tokens), len(right_tokens))

    def _snapshot_ids(self) -> list[tuple[str, MemoryRecord]]:
        records = self._store.list()
        finder = getattr(self._store, "find_id", None)
        pairs: list[tuple[str, MemoryRecord]] = []
        for record in records:
            record_id = finder(record) if finder else f"mem-{id(record)}"
            pairs.append((record_id, record))
        return pairs
