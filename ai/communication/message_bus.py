from __future__ import annotations

import asyncio
import contextlib
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

MessageHandler = Callable[[dict[str, Any]], Awaitable[None]]


class MessageBus:
    def __init__(self) -> None:
        self._subscriptions: dict[str, list[MessageHandler]] = {}
        self._history: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def send(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        message: dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "from": from_agent,
            "to": to_agent,
            "type": message_type,
            "payload": payload,
            "timestamp": time.time(),
        }

        async with self._lock:
            self._history.append(message)
            handlers = list(self._subscriptions.get(to_agent, []))

        for handler in handlers:
            with contextlib.suppress(Exception):
                await handler(message)

        return message

    async def subscribe(self, agent_id: str, handler: MessageHandler) -> None:
        async with self._lock:
            if agent_id not in self._subscriptions:
                self._subscriptions[agent_id] = []
            self._subscriptions[agent_id].append(handler)

    async def unsubscribe(self, agent_id: str, handler: MessageHandler) -> None:
        async with self._lock:
            handlers = self._subscriptions.get(agent_id, [])
            if handler in handlers:
                handlers.remove(handler)

    async def broadcast(
        self,
        sender: str,
        message_type: str,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        messages = []
        async with self._lock:
            subscribers = list(self._subscriptions.keys())
        for agent_id in subscribers:
            msg = await self.send(sender, agent_id, message_type, payload)
            messages.append(msg)
        return messages

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]
