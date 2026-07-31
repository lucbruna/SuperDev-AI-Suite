from __future__ import annotations

from typing import Any


class Broadcast:
    """Broadcasts messages to all agents."""

    def __init__(self) -> None:
        self._broadcast_count: int = 0

    @property
    def broadcast_count(self) -> int:
        return self._broadcast_count

    def send(self, sender: str, content: dict[str, Any], recipients: list[str]) -> int:
        self._broadcast_count += 1
        return len(recipients)

    def reset(self) -> None:
        self._broadcast_count = 0
