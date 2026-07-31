from __future__ import annotations

from typing import Any


class Unicast:
    """One-to-one message between agents."""

    def __init__(self) -> None:
        self._sent_count: int = 0

    @property
    def sent_count(self) -> int:
        return self._sent_count

    def send(self, sender: str, recipient: str, content: dict[str, Any]) -> bool:
        self._sent_count += 1
        return True

    def reset(self) -> None:
        self._sent_count = 0
