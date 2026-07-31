"""Payment webhooks."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class WebhookManager:
    def __init__(self) -> None:
        self._webhooks: dict[str, dict[str, Any]] = {}
        self._handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}
        self._log: list[dict[str, Any]] = []

    def register(self, event: str, url: str, secret: str = "") -> dict[str, Any]:
        webhook = {"event": event, "url": url, "secret": secret, "active": True}
        self._webhooks[f"{event}:{url}"] = webhook
        return webhook

    def add_handler(self, event: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        self._handlers[event] = handler

    def trigger(self, event: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        for _key, wh in self._webhooks.items():
            if wh["event"] == event and wh["active"]:
                self._log.append({"event": event, "url": wh["url"], "timestamp": __import__("time").time()})
                results.append({"url": wh["url"], "status": "sent"})
        handler = self._handlers.get(event)
        if handler:
            try:
                handler(data)
                results.append({"handler": event, "status": "executed"})
            except Exception as e:
                results.append({"handler": event, "status": "error", "error": str(e)})
        return results

    def list_webhooks(self) -> list[dict[str, Any]]:
        return list(self._webhooks.values())

    def deactivate(self, event: str, url: str) -> bool:
        key = f"{event}:{url}"
        if key in self._webhooks:
            self._webhooks[key]["active"] = False
            return True
        return False

    def get_log(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._log[-limit:]

    def remove(self, event: str, url: str) -> bool:
        key = f"{event}:{url}"
        if key in self._webhooks:
            del self._webhooks[key]
            return True
        return False
