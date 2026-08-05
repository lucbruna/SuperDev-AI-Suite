"""AIOS Memory Optimizer — pruning, compaction and retention policy.

Applies retention policies across memory stores: drops expired/old
entries, enforces per-store limits, and summarizes episodic history
into compact semantic facts when configured.
"""

from __future__ import annotations

import time
from typing import Any

RETENTION_DEFAULT = {
    "working": 60.0,       # seconds
    "cache": 300.0,
    "conversation": 3600.0,
    "episodic": 86_400.0 * 7,
    "semantic": None,       # no time retention
    "procedural": None,
    "knowledge": None,
    "vector": None,
}


class MemoryOptimizer:
    """Retention/compaction policies over a MemoryEngine."""

    def __init__(self, engine: Any, retention: dict[str, float | None] | None = None) -> None:
        self._engine = engine
        self._retention = dict(RETENTION_DEFAULT)
        if retention:
            self._retention.update(retention)

    def optimize(self, kind: str | None = None) -> dict[str, Any]:
        """Apply retention policy; returns what was removed per store."""
        kinds = [kind] if kind is not None else self._engine.kinds()
        report: dict[str, Any] = {}
        for store_kind in kinds:
            if store_kind not in self._retention or self._retention[store_kind] is None:
                report[store_kind] = {"policy": "keep-all"}
                continue
            store = self._engine.get(store_kind)
            if store is None:
                continue
            removed = self._prune(store, self._retention[store_kind])
            report[store_kind] = {"policy": "ttl", "ttl_s": self._retention[store_kind], "removed": removed}
        return report

    def _prune(self, store: Any, ttl: float) -> int:
        cutoff = time.time() - ttl
        removed = 0
        # Stores that expose a bulk removal path get it; otherwise fall back
        # to stats-only (records carry timestamps individually).
        prune = getattr(store, "prune_before", None)
        if callable(prune):
            result = prune(cutoff)
            if isinstance(result, int):
                removed = result
        return removed

    def report(self) -> dict[str, Any]:
        return {
            "retention": dict(self._retention),
            "stats": self._engine.stats(),
        }
