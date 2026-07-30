from __future__ import annotations

import json
import time
import zlib
from typing import Any, Dict, List, Optional, Set

from .memory_models import MemoryEntry
from .memory_types import ConsolidationStrategy, MemoryData


class MemoryOptimizer:
    """Optimization strategies for memory including dedup, compression, and pruning."""

    def __init__(self, strategy: ConsolidationStrategy = ConsolidationStrategy.MERGE):
        self._strategy = strategy
        self._stats: Dict[str, int] = {"dedup": 0, "compressed": 0, "pruned": 0, "merged": 0}

    @property
    def strategy(self) -> ConsolidationStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, value: ConsolidationStrategy) -> None:
        self._strategy = value

    @property
    def stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def deduplicate(self, entries: List[MemoryEntry]) -> List[MemoryEntry]:
        seen: Set[int] = set()
        unique: List[MemoryEntry] = []
        for entry in entries:
            data_hash = self._hash_data(entry.data)
            if data_hash not in seen:
                seen.add(data_hash)
                unique.append(entry)
            else:
                self._stats["dedup"] += 1
        return unique

    def compress(self, data: MemoryData) -> bytes:
        raw = json.dumps(data, sort_keys=True).encode("utf-8")
        compressed = zlib.compress(raw, level=6)
        self._stats["compressed"] += 1
        return compressed

    def decompress(self, compressed: bytes) -> MemoryData:
        raw = zlib.decompress(compressed)
        return json.loads(raw.decode("utf-8"))

    def prune_expired(self, entries: List[MemoryEntry]) -> List[MemoryEntry]:
        active = [e for e in entries if not e.is_expired]
        self._stats["pruned"] += len(entries) - len(active)
        return active

    def prune_by_age(self, entries: List[MemoryEntry], max_age: float) -> List[MemoryEntry]:
        now = time.time()
        kept = [e for e in entries if now - e.created_at <= max_age]
        self._stats["pruned"] += len(entries) - len(kept)
        return kept

    def prune_by_priority(self, entries: List[MemoryEntry], min_priority: int) -> List[MemoryEntry]:
        kept = [e for e in entries if e.priority >= min_priority]
        self._stats["pruned"] += len(entries) - len(kept)
        return kept

    def merge(self, entries: List[MemoryEntry]) -> MemoryEntry | None:
        if not entries:
            return None
        base = entries[0]
        merged_data: MemoryData = dict(base.data)
        for entry in entries[1:]:
            merged_data.update(entry.data)
        merged_entry = MemoryEntry(
            key=base.key,
            data=merged_data,
            scope=base.scope,
            category=base.category,
            tags=list({t for e in entries for t in e.tags}),
            priority=max(e.priority for e in entries),
        )
        self._stats["merged"] += 1
        return merged_entry

    def consolidate(self, entries: List[MemoryEntry]) -> List[MemoryEntry]:
        if self._strategy == ConsolidationStrategy.DEDUP:
            return self.deduplicate(entries)
        elif self._strategy == ConsolidationStrategy.MERGE:
            grouped: Dict[str, List[MemoryEntry]] = {}
            for e in entries:
                grouped.setdefault(e.key, []).append(e)
            result: List[MemoryEntry] = []
            for group in grouped.values():
                merged = self.merge(group)
                if merged:
                    result.append(merged)
            return result
        elif self._strategy == ConsolidationStrategy.COMPRESS:
            return entries
        return entries

    def reset_stats(self) -> None:
        self._stats = {"dedup": 0, "compressed": 0, "pruned": 0, "merged": 0}

    def _hash_data(self, data: MemoryData) -> int:
        return hash(json.dumps(data, sort_keys=True))
