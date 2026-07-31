from __future__ import annotations

import time
from typing import Any


class Experience:
    """A single lived experience recorded by the AI."""

    def __init__(
        self,
        experience_id: str,
        summary: str,
        context: dict[str, Any] | None = None,
        outcome: str = "",
        tags: list[str] | None = None,
    ):
        self._experience_id = experience_id
        self._summary = summary
        self._context = context or {}
        self._outcome = outcome
        self._tags = tags or []
        self._timestamp = time.time()
        self._events: list[dict[str, Any]] = []
        self._importance: float = 0.0

    @property
    def experience_id(self) -> str:
        return self._experience_id

    @property
    def summary(self) -> str:
        return self._summary

    @property
    def context(self) -> dict[str, Any]:
        return dict(self._context)

    @property
    def outcome(self) -> str:
        return self._outcome

    @property
    def tags(self) -> list[str]:
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

    def add_event(self, event: dict[str, Any]) -> None:
        self._events.append(event)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experience_id": self._experience_id,
            "summary": self._summary,
            "outcome": self._outcome,
            "tags": list(self._tags),
            "timestamp": self._timestamp,
            "importance": self._importance,
            "event_count": len(self._events),
        }
