from __future__ import annotations

import time
from typing import Any


class Interaction:
    """A single recorded interaction."""

    def __init__(self, interaction_type: str, content: dict[str, Any]):
        self._type = interaction_type
        self._content = dict(content)
        self._timestamp = time.time()

    @property
    def interaction_type(self) -> str:
        return self._type

    @property
    def content(self) -> dict[str, Any]:
        return dict(self._content)

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self._type,
            "content": dict(self._content),
            "timestamp": self._timestamp,
        }


class InteractionHistory:
    """History of interactions within the current session."""

    def __init__(self, max_length: int = 1000):
        self._max_length = max_length
        self._interactions: list[Interaction] = []

    @property
    def max_length(self) -> int:
        return self._max_length

    @property
    def length(self) -> int:
        return len(self._interactions)

    def record(self, interaction_type: str, content: dict[str, Any]) -> None:
        interaction = Interaction(interaction_type, content)
        self._interactions.append(interaction)
        if len(self._interactions) > self._max_length:
            self._interactions.pop(0)

    def get_recent(self, count: int = 10) -> list[Interaction]:
        return list(self._interactions[-count:])

    def get_by_type(self, interaction_type: str) -> list[Interaction]:
        return [i for i in self._interactions if i.interaction_type == interaction_type]

    def get_since(self, timestamp: float) -> list[Interaction]:
        return [i for i in self._interactions if i.timestamp >= timestamp]

    def clear(self) -> None:
        self._interactions.clear()

    def to_dict_list(self) -> list[dict[str, Any]]:
        return [i.to_dict() for i in self._interactions]
