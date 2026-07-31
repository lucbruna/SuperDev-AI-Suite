"""Episodic memory for event sequences and experiences."""

from __future__ import annotations

import time
from typing import Any


class EpisodicMemory:
    """Stores time-ordered event sequences as episodes."""

    def __init__(self) -> None:
        self._episodes: dict[str, dict[str, Any]] = {}
        self._timeline: list[str] = []

    def store(self, key: str, value: Any, context: dict[str, Any] | None = None) -> None:
        self._episodes[key] = {
            "value": value,
            "context": context or {},
            "timestamp": time.time(),
            "episode_index": len(self._timeline),
        }
        self._timeline.append(key)

    def retrieve(self, key: str) -> Any | None:
        episode = self._episodes.get(key)
        if episode is None:
            return None
        return episode.get("value")

    def get_episode(self, key: str) -> dict[str, Any] | None:
        return self._episodes.get(key)

    def get_recent(self, count: int = 10) -> list[dict[str, Any]]:
        recent_keys = self._timeline[-count:]
        return [self._episodes[k] for k in recent_keys if k in self._episodes]

    def get_by_time_range(self, start: float, end: float) -> list[dict[str, Any]]:
        results = []
        for key in self._timeline:
            ep = self._episodes.get(key)
            if ep and start <= ep["timestamp"] <= end:
                results.append(ep)
        return results

    def remove(self, key: str) -> bool:
        removed = key in self._episodes
        self._episodes.pop(key, None)
        if key in self._timeline:
            self._timeline.remove(key)
        return removed

    def count(self) -> int:
        return len(self._episodes)

    def keys(self) -> list[str]:
        return list(self._timeline)

    def clear(self) -> None:
        self._episodes.clear()
        self._timeline.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "count": len(self._episodes),
            "timeline_length": len(self._timeline),
        }
