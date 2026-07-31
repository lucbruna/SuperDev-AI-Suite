"""Memory cleanup and garbage collection."""
from __future__ import annotations

import time
from typing import Any, Dict


class MemoryCleanup:
    """Cleanup and garbage collection for memory subsystems."""

    def __init__(self) -> None:
        self._cleanup_count: int = 0
        self._total_removed: int = 0

    def cleanup_all(self, memory_engine: Any,
                    max_age_hours: int = 168) -> Dict[str, Any]:
        max_age_seconds = max_age_hours * 3600
        now = time.time()
        removed = 0
        for backend_name in ["short_term", "long_term", "episodic", "semantic"]:
            backend = getattr(memory_engine, backend_name, None)
            if backend is None:
                continue
            if hasattr(backend, "count") and hasattr(backend, "get_all"):
                items = {}
                if hasattr(backend, "_store"):
                    items = backend._store
                for key in list(items.keys()):
                    entry = items[key]
                    ts = entry.get("timestamp", 0) if isinstance(entry, dict) else 0
                    if now - ts > max_age_seconds:
                        backend.remove(key)
                        removed += 1
        self._cleanup_count += 1
        self._total_removed += removed
        return {
            "entries_removed": removed,
            "cleanup_number": self._cleanup_count,
        }

    def cleanup_short_term(self, memory_engine: Any) -> Dict[str, Any]:
        st = memory_engine.short_term
        before = st.count()
        excess = before - st._max_size if hasattr(st, "_max_size") else 0
        return {"short_term_before": before, "excess_evicted": max(0, excess)}

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_cleanups": self._cleanup_count,
            "total_entries_removed": self._total_removed,
        }

    def snapshot(self) -> Dict[str, Any]:
        return self.get_stats()
