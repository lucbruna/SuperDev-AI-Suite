from __future__ import annotations

import asyncio
import json
from typing import Any

from backend.audit.audit_logger import AuditLogger


class AuditStream:
    def __init__(self, logger: AuditLogger | None = None):
        self._logger = logger or AuditLogger()
        self._subscribers: dict[str, asyncio.Queue] = {}
        self._running = False

    async def start(self):
        self._running = True

    async def stop(self):
        self._running = False
        self._subscribers.clear()

    async def emit(self, event: dict[str, Any]):
        if not self._running:
            return
        await self._logger.log(
            action=event.get("action", "UNKNOWN"),
            resource_type=event.get("resource_type", "unknown"),
            resource_id=event.get("resource_id", ""),
            user_id=event.get("user_id", "system"),
            details=event.get("details", {}),
            ip_address=event.get("ip_address", "127.0.0.1"),
            severity=event.get("severity", "info"),
            success=event.get("success", True),
        )
        serialized = json.dumps(event, default=str)
        for sub_id, queue in list(self._subscribers.items()):
            try:
                await asyncio.wait_for(queue.put(serialized), timeout=1.0)
            except (asyncio.TimeoutError, asyncio.QueueFull):
                pass

    async def subscribe(self) -> tuple[str, asyncio.Queue]:
        import uuid
        sub_id = str(uuid.uuid4())
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers[sub_id] = queue
        return sub_id, queue

    async def unsubscribe(self, sub_id: str):
        self._subscribers.pop(sub_id, None)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)