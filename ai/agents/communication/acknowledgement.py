from __future__ import annotations

import time
from typing import Any, Dict, Optional


class Acknowledgement:
    """Acknowledgement tracking for messages."""

    def __init__(self) -> None:
        self._acks: Dict[str, float] = {}

    def acknowledge(self, msg_id: str) -> None:
        self._acks[msg_id] = time.time()

    def is_acknowledged(self, msg_id: str) -> bool:
        return msg_id in self._acks

    def ack_time(self, msg_id: str) -> Optional[float]:
        return self._acks.get(msg_id)

    def clear(self) -> None:
        self._acks.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {"acknowledged_count": len(self._acks)}
