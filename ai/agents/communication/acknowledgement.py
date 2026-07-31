from __future__ import annotations

import time
from typing import Any


class Acknowledgement:
    """Acknowledgement tracking for messages."""

    def __init__(self) -> None:
        self._acks: dict[str, float] = {}

    def acknowledge(self, msg_id: str) -> None:
        self._acks[msg_id] = time.time()

    def is_acknowledged(self, msg_id: str) -> bool:
        return msg_id in self._acks

    def ack_time(self, msg_id: str) -> float | None:
        return self._acks.get(msg_id)

    def clear(self) -> None:
        self._acks.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"acknowledged_count": len(self._acks)}
