"""Index entry updates (term dictionaries)."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import (IndexEntry, IndexStatus)
from enterprise_knowledge.knowledge_protocols import new_id, tokenize
from enterprise_knowledge.knowledge_registry import EnterpriseKnowledgeRegistry


class IndexUpdater:
    """Builds and mutates term-frequency index entries."""

    def __init__(self, registry: EnterpriseKnowledgeRegistry | None = None,
                 stopwords: set[str] | None = None) -> None:
        self.registry = registry
        self.stopwords = stopwords or {
            "de", "da", "do", "e", "o", "a", "os", "as", "um", "uma",
            "em", "com", "para", "por", "que", "ao", "no", "na",
        }

    def build_terms(self, text: str) -> dict[str, int]:
        terms: dict[str, int] = {}
        for token in tokenize(text):
            if len(token) < 3 or token in self.stopwords:
                continue
            terms[token] = terms.get(token, 0) + 1
        return terms

    def upsert(self, target_id: str, text: str,
               index_id: str = "") -> IndexEntry | None:
        if self.registry is None:
            return None
        entry = IndexEntry(index_id=index_id or new_id("index"),
                           target_id=target_id,
                           terms=self.build_terms(text),
                           status=IndexStatus.SYNCED,
                           updated_at=time.time())
        self.registry.register_index(entry)
        return entry

    def mark_stale(self, target_id: str) -> bool:
        if self.registry is None:
            return False
        for index_id in self.registry.list_index():
            entry = self.registry.get_index(index_id)
            if entry is not None and entry.target_id == target_id:
                entry.status = IndexStatus.STALE
                return True
        return False
