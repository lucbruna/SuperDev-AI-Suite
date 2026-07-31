from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable


class IntegrationEventType(str, Enum):
    CONNECTION_CREATED = "integration.connection_created"
    CONNECTION_CONNECTED = "integration.connection_connected"
    CONNECTION_DISCONNECTED = "integration.connection_disconnected"
    CONNECTION_ERROR = "integration.connection_error"
    API_REGISTERED = "integration.api_registered"
    WEBHOOK_RECEIVED = "integration.webhook_received"
    WEBHOOK_DELIVERED = "integration.webhook_delivered"
    EVENT_PUBLISHED = "integration.event_published"
    MESSAGE_ENQUEUED = "integration.message_enqueued"
    SYNC_COMPLETED = "integration.sync_completed"
    TRANSFORMED = "integration.transformed"
    INTEGRATION_INSTALLED = "integration.installed"
    ALERT_RAISED = "integration.alert_raised"
    ERROR = "integration.error"


class IntegrationEvents:
    """Emits and subscribes to integration lifecycle events."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.events")
        self._listeners: dict[str, list[Callable[..., Any]]] = {}

    def emit(self, event_type: str, payload: dict[str, Any] | None = None) -> None:
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(event_type=event_type, payload=payload or {})
            except Exception as exc:  # noqa: BLE001 - listener isolation
                self._log.warning("listener failed for %s: %s", event_type, exc)

    def on(self, event_type: str, listener: Callable[..., Any]) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def off(self, event_type: str, listener: Callable[..., Any]) -> None:
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
            except ValueError:
                pass

    def once(self, event_type: str, listener: Callable[..., Any]) -> None:
        def _wrapper(**kwargs: Any) -> None:
            self.off(event_type, _wrapper)
            listener(**kwargs)

        self.on(event_type, _wrapper)

    def listener_count(self, event_type: str) -> int:
        return len(self._listeners.get(event_type, []))
