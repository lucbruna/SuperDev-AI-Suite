from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class Episode:
    """A grouped episode consisting of multiple events."""

    def __init__(self, episode_id: str, name: str, metadata: Dict[str, Any] | None = None):
        self._episode_id = episode_id
        self._name = name
        self._metadata = metadata or {}
        self._events: List[Dict[str, Any]] = []
        self._started_at = time.time()
        self._ended_at: float | None = None

    @property
    def episode_id(self) -> str:
        return self._episode_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    @property
    def events(self) -> List[Dict[str, Any]]:
        return list(self._events)

    @property
    def started_at(self) -> float:
        return self._started_at

    @property
    def ended_at(self) -> float | None:
        return self._ended_at

    @property
    def duration(self) -> float | None:
        if self._ended_at is None:
            return None
        return self._ended_at - self._started_at

    @property
    def is_active(self) -> bool:
        return self._ended_at is None

    def add_event(self, event: Dict[str, Any]) -> None:
        self._events.append(event)

    def end(self) -> None:
        self._ended_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "episode_id": self._episode_id,
            "name": self._name,
            "metadata": dict(self._metadata),
            "event_count": len(self._events),
            "started_at": self._started_at,
            "ended_at": self._ended_at,
            "duration": self.duration,
            "is_active": self.is_active,
        }


class Episodes:
    """Manager for grouped episodic experiences."""

    def __init__(self):
        self._episodes: Dict[str, Episode] = {}

    @property
    def count(self) -> int:
        return len(self._episodes)

    def start(self, episode_id: str, name: str, metadata: Dict[str, Any] | None = None) -> Episode:
        episode = Episode(episode_id, name, metadata)
        self._episodes[episode_id] = episode
        return episode

    def end(self, episode_id: str) -> bool:
        episode = self._episodes.get(episode_id)
        if episode is None:
            return False
        episode.end()
        return True

    def get(self, episode_id: str) -> Episode | None:
        return self._episodes.get(episode_id)

    def get_active(self) -> List[Episode]:
        return [e for e in self._episodes.values() if e.is_active]

    def get_completed(self) -> List[Episode]:
        return [e for e in self._episodes.values() if not e.is_active]

    def remove(self, episode_id: str) -> bool:
        return self._episodes.pop(episode_id, None) is not None

    def clear(self) -> None:
        self._episodes.clear()
