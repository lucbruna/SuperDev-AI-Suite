from __future__ import annotations

import asyncio
from typing import Any

from agents.communication.message_bus import MessageBus


class StateSynchronizer:
    def __init__(self, bus: MessageBus | None = None):
        self._bus = bus or MessageBus()
        self._states: dict[str, dict[str, Any]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _lock(self, key: str) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def update_state(self, agent_id: str, key: str, value: Any) -> None:
        async with self._lock(key):
            if key not in self._states:
                self._states[key] = {}
            self._states[key][agent_id] = {"value": value, "timestamp": __import__("time").time()}
            await self._bus.publish("sync.state_updated", {"key": key, "agent_id": agent_id})

    async def get_state(self, key: str) -> dict[str, Any]:
        async with self._lock(key):
            return dict(self._states.get(key, {}))

    async def get_merged_state(self, key: str) -> Any | None:
        async with self._lock(key):
            entries = self._states.get(key, {})
            if not entries:
                return None
            latest = max(entries.values(), key=lambda e: e["timestamp"])
            return latest["value"]

    async def wait_for_key(self, key: str, timeout: float = 30.0) -> Any:
        start = __import__("time").time()
        while True:
            result = await self.get_merged_state(key)
            if result is not None:
                return result
            if __import__("time").time() - start > timeout:
                raise TimeoutError(f"Timeout waiting for key: {key}")
            await asyncio.sleep(0.1)

    async def clear_key(self, key: str) -> None:
        async with self._lock(key):
            self._states.pop(key, None)

    async def list_keys(self) -> list[str]:
        return list(self._states.keys())

    async def get_all_states(self) -> dict[str, dict[str, Any]]:
        return {k: dict(v) for k, v in self._states.items()}