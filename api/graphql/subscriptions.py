from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Callable

from ..api_events import APIEventBus


class SubscriptionManager:
    """Manages GraphQL subscriptions (real-time event sources)."""

    def __init__(self, events: APIEventBus | None = None) -> None:
        self._subscriptions: dict[str, dict[str, Any]] = {}
        self._topic_subscribers: dict[str, list[str]] = {}
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

    def subscribe(self, subscriber_id: str, topic: str) -> bool:
        subscribers = self._topic_subscribers.setdefault(topic, [])
        if subscriber_id not in subscribers:
            subscribers.append(subscriber_id)
        return True

    def get_subscribers(self, topic: str) -> list[str]:
        return list(self._topic_subscribers.get(topic, []))

    def unsubscribe(self, subscriber_id: str, topic: str | None = None) -> bool:
        if topic is not None:
            subscribers = self._topic_subscribers.get(topic)
            if subscribers is None:
                return False
            if subscriber_id in subscribers:
                subscribers.remove(subscriber_id)
            return True
        removed = False
        for subscribers in self._topic_subscribers.values():
            if subscriber_id in subscribers:
                subscribers.remove(subscriber_id)
                removed = True
        return removed

    def list_subscriptions(self) -> list[dict[str, Any]]:
        return [
            {"name": s["name"], "description": s["description"], "active": len(s["subscribers"])}
            for s in self._subscriptions.values()
        ]

    def to_dict(self) -> dict[str, Any]:
        return {"subscriptions": self.list_subscriptions(), "count": len(self._subscriptions)}
