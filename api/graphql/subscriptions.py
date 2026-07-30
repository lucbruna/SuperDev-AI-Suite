from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Callable

from ..api_events import APIEventBus


class SubscriptionManager:
    """Manages GraphQL subscriptions (real-time event sources)."""

    def __init__(self, events: APIEventBus | None = None) -> None:
        self._subscriptions: dict[str, dict[str, Any]] = {}
        self._events = events

    def register(
        self,
        name: str,
        subscribe_fn: Callable[[Any], AsyncIterator[Any]],
        description: str = "",
    ) -> None:
        self._subscriptions[name] = {
            "name": name,
            "subscribe": subscribe_fn,
            "description": description,
            "subscribers": [],
        }

    def subscribe(self, name: str, context: Any = None) -> AsyncIterator[Any] | None:
        sub = self._subscriptions.get(name)
        if sub is None:
            return None
        return sub["subscribe"](context)

    def unsubscribe(self, name: str, subscriber_id: str) -> bool:
        sub = self._subscriptions.get(name)
        if sub is None:
            return False
        sub["subscribers"] = [s for s in sub["subscribers"] if s != subscriber_id]
        return True

    def list_subscriptions(self) -> list[dict[str, Any]]:
        return [
            {"name": s["name"], "description": s["description"], "active": len(s["subscribers"])}
            for s in self._subscriptions.values()
        ]

    def to_dict(self) -> dict[str, Any]:
        return {"subscriptions": self.list_subscriptions(), "count": len(self._subscriptions)}
