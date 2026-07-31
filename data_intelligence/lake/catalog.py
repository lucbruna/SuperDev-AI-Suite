"""Lake catalog (metadata registry)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class LakeEntry:
    """Metadata for an object stored in the lake."""

    key: str
    zone: str
    size_bytes: int = 0
    compressed: bool = False
    partition: str | None = None
    ingested_at: str = field(default_factory=lambda: datetime.now(
        timezone.utc).isoformat())


class LakeCatalog:
    """Tracks metadata for every lake object."""

    def __init__(self) -> None:
        self._entries: dict[str, LakeEntry] = {}

    def add(self, entry: LakeEntry) -> None:
        self._entries[entry.key] = entry

    def get(self, key: str) -> LakeEntry | None:
        return self._entries.get(key)

    def remove(self, key: str) -> bool:
        return self._entries.pop(key, None) is not None

    def search(self, zone: str | None = None,
               partition: str | None = None) -> list[LakeEntry]:
        entries = list(self._entries.values())
        if zone is not None:
            entries = [e for e in entries if e.zone == zone]
        if partition is not None:
            entries = [e for e in entries if e.partition == partition]
        return entries

    def stats(self) -> dict[str, Any]:
        return {"total_objects": len(self._entries),
                "zones": sorted({e.zone for e in self._entries.values()}),
                "total_bytes": sum(e.size_bytes for e in
                                   self._entries.values())}
