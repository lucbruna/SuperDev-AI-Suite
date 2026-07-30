from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class TimelineEntry:
    """A single point on the timeline."""

    def __init__(self, entry_type: str, data: Dict[str, Any]):
        self._type = entry_type
        self._data = dict(data)
        self._timestamp = time.time()

    @property
    def entry_type(self) -> str:
        return self._type

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self._type,
            "data": dict(self._data),
            "timestamp": self._timestamp,
        }


class Timeline:
    """Chronological timeline of episodic events."""

    def __init__(self):
        self._entries: List[TimelineEntry] = []

    @property
    def count(self) -> int:
        return len(self._entries)

    def add(self, entry_type: str, data: Dict[str, Any]) -> TimelineEntry:
        entry = TimelineEntry(entry_type, data)
        self._entries.append(entry)
        return entry

    def get_since(self, timestamp: float) -> List[TimelineEntry]:
        return [e for e in self._entries if e.timestamp >= timestamp]

    def get_between(self, start: float, end: float) -> List[TimelineEntry]:
        return [e for e in self._entries if start <= e.timestamp <= end]

    def get_by_type(self, entry_type: str) -> List[TimelineEntry]:
        return [e for e in self._entries if e.entry_type == entry_type]

    def get_recent(self, count: int = 50) -> List[TimelineEntry]:
        return list(self._entries[-count:])

    def clear(self) -> None:
        self._entries.clear()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._entries]
