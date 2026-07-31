from __future__ import annotations

import time
from collections.abc import Callable
from enum import Enum
from typing import Any


class LLMEventType(Enum):
    REQUEST_START = "request_start"
    REQUEST_COMPLETE = "request_complete"
    REQUEST_ERROR = "request_error"
    PROVIDER_REGISTERED = "provider_registered"
    PROVIDER_UNREGISTERED = "provider_unregistered"
    PROVIDER_ERROR = "provider_error"
    ROUTE_SELECTED = "route_selected"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    TOKEN_LIMIT = "token_limit"
    COST_LIMIT = "cost_limit"
    MODERATION_FLAG = "moderation_flag"


class LLMEventBus:
    """Simple event bus for LLM layer events."""

    def __init__(self) -> None:
        self._handlers: dict[LLMEventType, list[Callable]] = {}

    def on(self, event_type: LLMEventType, handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def off(self, event_type: LLMEventType, handler: Callable) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def emit(self, event_type: LLMEventType, data: dict[str, Any] | None = None) -> None:
        handlers = self._handlers.get(event_type, [])
        payload = {
            "event": event_type.value,
            "timestamp": time.time(),
            "data": data or {},
        }
        for handler in handlers:
            try:
                result = handler(payload)
                if hasattr(result, "__await__"):
                    await result
            except Exception:
                pass

    def to_dict(self) -> dict[str, Any]:
        return {
            "registered_events": [e.value for e in self._handlers],
            "handler_count": sum(len(h) for h in self._handlers.values()),
        }
