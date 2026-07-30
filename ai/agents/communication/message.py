from __future__ import annotations

import time
from typing import Any, Dict


class Message:
    """A single message between agents."""

    def __init__(self, sender: str, recipient: str, msg_type: str, payload: Dict[str, Any]) -> None:
        self._msg_id = f"{sender}_{recipient}_{time.time()}"
        self._sender = sender
        self._recipient = recipient
        self._msg_type = msg_type
        self._payload = payload
        self._timestamp = time.time()

    @property
    def msg_id(self) -> str:
        return self._msg_id

    @property
    def sender(self) -> str:
        return self._sender

    @property
    def recipient(self) -> str:
        return self._recipient

    @property
    def msg_type(self) -> str:
        return self._msg_type

    @property
    def payload(self) -> Dict[str, Any]:
        return dict(self._payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self._msg_id,
            "sender": self._sender,
            "recipient": self._recipient,
            "type": self._msg_type,
            "payload": self._payload,
            "timestamp": self._timestamp,
        }
