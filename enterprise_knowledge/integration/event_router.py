"""Typed event routing for knowledge events."""

from __future__ import annotations

from typing import Any, Callable

from enterprise_knowledge.knowledge_events import EnterpriseKnowledgeEventType

_Handler = Callable[[dict[str, Any]], None]


class EventRouter:
    """Routes events to handlers registered per event type."""

    def __init__(self) -> None:
        self._handlers: dict[EnterpriseKnowledgeEventType, list[_Handler]] = {}

    def on(self, event_type: EnterpriseKnowledgeEventType,
           handler: _Handler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def off(self, event_type: EnterpriseKnowledgeEventType,
            handler: _Handler) -> None:
        handlers = self._handlers.get(event_type)
        if handlers is not None and handler in handlers:
            handlers.remove(handler)
            if not handlers:
                del self._handlers[event_type]

    def route(self, event_type: EnterpriseKnowledgeEventType,
              payload: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for handler in list(self._handlers.get(event_type, [])):
            try:
                handler(payload)
                results.append({"ok": True, "handler": getattr(
                    handler, "__name__", "anonymous")})
            except Exception as exc:  # noqa: BLE001 - isolate handlers
                results.append({"ok": False, "handler": getattr(
                    handler, "__name__", "anonymous"), "error": str(exc)})
        return results

    def counts(self) -> dict[str, int]:
        return {event_type.value: len(handlers)
                for event_type, handlers in self._handlers.items()}
