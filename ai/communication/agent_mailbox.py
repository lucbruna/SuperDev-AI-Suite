from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any


class AgentMailbox:
    def __init__(self, agent_id: str) -> None:
        self._agent_id = agent_id
        self._messages: list[dict[str, Any]] = []
        self._read_ids: set[str] = set()
        self._lock = asyncio.Lock()

    def has_messages(self) -> bool:
        return len(self._messages) > 0

    async def get_messages(self) -> list[dict[str, Any]]:
        async with self._lock:
            return list(self._messages)

    async def send_message(self, message: dict[str, Any]) -> dict[str, Any]:
        msg: dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "to": self._agent_id,
            "timestamp": time.time(),
            "read": False,
            **message,
        }
        async with self._lock:
            self._messages.append(msg)
        return msg

    async def mark_read(self, message_id: str) -> None:
        async with self._lock:
            self._read_ids.add(message_id)
            for msg in self._messages:
                if msg.get("id") == message_id:
                    msg["read"] = True

    async def get_unread_count(self) -> int:
        async with self._lock:
            return sum(1 for m in self._messages if not m.get("read"))

    async def clear(self) -> None:
        async with self._lock:
            self._messages.clear()
            self._read_ids.clear()
