from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Awaitable, Callable

from ..api_logger import APILogger
from .event_bus import Event, EventBus

CallbackHandler = Callable[..., Awaitable[Any]]


class CallbackManager:
    """Manages callback registrations and invocations triggered by events."""

    def __init__(self, event_bus: EventBus, logger: APILogger | None = None) -> None:
        self._event_bus = event_bus
        self._logger = logger or APILogger(__name__)
        self._callbacks: dict[str, list[dict[str, Any]]] = {}
        self._timeout: float = 30.0

    def register(
        self,
        event_topic: str,
        handler: CallbackHandler,
        *,
        callback_id: str | None = None,
        timeout: float | None = None,
        max_invocations: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        cb_id = callback_id or uuid.uuid4().hex
        entry: dict[str, Any] = {
            "id": cb_id,
            "handler": handler,
            "timeout": timeout or self._timeout,
            "max_invocations": max_invocations,
            "invocations": 0,
            "metadata": metadata or {},
            "created_at": time.time(),
        }
        self._callbacks.setdefault(event_topic, []).append(entry)
        self._event_bus.subscribe(event_topic, self._make_dispatcher(entry))
        self._logger.info(f"Registered callback '{cb_id}' for event '{event_topic}'")
        return cb_id

    def _make_dispatcher(self, entry: dict[str, Any]) -> Callable[[Event], Awaitable[Any]]:
        async def dispatcher(event: Event) -> Any:
            handler: CallbackHandler = entry["handler"]
            try:
                result = await asyncio.wait_for(
                    handler(event=event, metadata=entry["metadata"]),
                    timeout=entry["timeout"],
                )
                entry["invocations"] += 1
                if entry["max_invocations"] and entry["invocations"] >= entry["max_invocations"]:
                    self.unregister(entry["id"])
                return result
            except asyncio.TimeoutError:
                self._logger.warning(f"Callback '{entry['id']}' timed out after {entry['timeout']}s")
                raise
            except Exception as exc:
                self._logger.error(f"Callback '{entry['id']}' failed: {exc}")
                raise

        return dispatcher

    def unregister(self, callback_id: str) -> bool:
        for topic, callbacks in self._callbacks.items():
            for i, entry in enumerate(callbacks):
                if entry["id"] == callback_id:
                    callbacks.pop(i)
                    if not callbacks:
                        del self._callbacks[topic]
                    self._logger.info(f"Unregistered callback '{callback_id}'")
                    return True
        return False

    def get_callbacks(self, event_topic: str | None = None) -> list[dict[str, Any]]:
        if event_topic:
            return [
                {k: v for k, v in cb.items() if k != "handler"}
                for cb in self._callbacks.get(event_topic, [])
            ]
        result: list[dict[str, Any]] = []
        for callbacks in self._callbacks.values():
            for cb in callbacks:
                result.append({k: v for k, v in cb.items() if k != "handler"})
        return result

    def get_callback(self, callback_id: str) -> dict[str, Any] | None:
        for callbacks in self._callbacks.values():
            for cb in callbacks:
                if cb["id"] == callback_id:
                    return {k: v for k, v in cb.items() if k != "handler"}
        return None

    def clear(self) -> None:
        self._callbacks.clear()
