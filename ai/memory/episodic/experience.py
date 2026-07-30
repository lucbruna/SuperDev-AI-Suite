from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class Experience:
    """A single lived experience recorded by the AI."""

    def __init__(
        self,
        experience_id: str,
        summary: str,
        context: Dict[str, Any] | None = None,
        outcome: str = "",
        tags: List[str] | None = None,
    ):
        self._experience_id = experience_id
        self._summary = summary
        self._context = context or {}
        self._outcome = outcome
        self._tags = tags or []
        self._timestamp = time.time()
        self._events: List[Dict[str, Any]] = []
        self._importance: float = 0.0

    @property
    def experience_id(self) -> str:
        return self._experience_id

    @property
    def summary(self) -> str:
        return self._summary

    @property
    def context(self) -> Dict[str, Any]:
        return dict(self._context)

    @property
    def outcome(self) -> str:
        return self._outcome

    @property
    def tags(self) -> List[str]:
        return list(self._tags)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def importance(self) -> float:
        return self._importance

    @importance.setter
    def importance(self, value: float) -> None:
        self._importance = max(0.0, min(1.0, value))

    def add_event(self, event: Dict[str, Any]) -> None:
        self._events.append(event)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experience_id": self._experience_id,
            "summary": self._summary,
            "outcome": self._outcome,
            "tags": list(self._tags),
            "timestamp": self._timestamp,
            "importance": self._importance,
            "event_count": len(self._events),
        }
