from __future__ import annotations

from typing import Any, Dict, List

from .archive_manager import ArchiveManager
from .cleanup_scheduler import CleanupScheduler
from .decay import Decay
from .expiration_policy import ExpirationPolicy
from .garbage_collector import GarbageCollector
from .redundancy_detector import RedundancyDetector
from .retention_policy import RetentionPolicy


class ForgettingEngine:
    """Facade for intelligent forgetting — decay, expiration, cleanup."""

    def __init__(self):
        self._expiration = ExpirationPolicy()
        self._decay = Decay()
        self._gc = GarbageCollector()
        self._scheduler = CleanupScheduler()
        self._redundancy = RedundancyDetector()
        self._archive = ArchiveManager()
        self._retention = RetentionPolicy()
        self._forgetting_count: int = 0

    @property
    def expiration(self) -> ExpirationPolicy:
        return self._expiration

    @property
    def decay(self) -> Decay:
        return self._decay

    @property
    def gc(self) -> GarbageCollector:
        return self._gc

    @property
    def scheduler(self) -> CleanupScheduler:
        return self._scheduler

    @property
    def redundancy(self) -> RedundancyDetector:
        return self._redundancy

    @property
    def archive(self) -> ArchiveManager:
        return self._archive

    @property
    def retention(self) -> RetentionPolicy:
        return self._retention

    def run_forgetting_cycle(self, entries: Dict[str, Any]) -> Dict[str, Any]:
        expired = self._expiration.find_expired(entries)
        decayed = self._decay.apply_decay(entries)
        redundant = self._redundancy.find_redundant(entries)
        to_remove = set(expired.keys()) | set(decayed.keys()) | set(redundant.keys())
        kept = {k: v for k, v in entries.items() if k not in to_remove}
        archived = {k: entries[k] for k in list(to_remove)[:5]}
        for key, value in archived.items():
            self._archive.archive(key, value)
        self._forgetting_count += 1
        return {
            "removed_count": len(to_remove),
            "archived_count": len(archived),
            "kept_count": len(kept),
            "cycle": self._forgetting_count,
        }

    def snapshot(self) -> Dict[str, Any]:
        return {
            "forgetting_cycles": self._forgetting_count,
            "archived_entries": self._archive.archived_count,
            "scheduled_cleanups": self._scheduler.task_count,
        }
