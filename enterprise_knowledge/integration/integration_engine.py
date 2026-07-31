"""Integration engine: API bridge, event routing and webhooks."""

from __future__ import annotations

from typing import Any, Callable

from enterprise_knowledge.integration.api_bridge import ApiBridge
from enterprise_knowledge.integration.event_router import EventRouter
from enterprise_knowledge.integration.webhook_dispatcher import WebhookDispatcher
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics

_Handler = Callable[[dict[str, Any]], None]
_Operation = Callable[..., Any]


class IntegrationEngine:
    """Exposes the knowledge engine to external systems."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None) -> None:
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.bridge = ApiBridge(events=self.events, metrics=self.metrics)
        self.router = EventRouter()
        self.webhooks = WebhookDispatcher(metrics=self.metrics)

    # -- API bridge ----------------------------------------------------------
    def register_operation(self, name: str, operation: _Operation) -> None:
        self.bridge.register(name, operation)

    def operations(self) -> list[str]:
        return self.bridge.operations()

    def handle_api(self, operation: str,
                   params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.bridge.handle(operation, params)

    # -- event routing -------------------------------------------------------
    def on_event(self, event_type: EnterpriseKnowledgeEventType,
                 handler: _Handler) -> None:
        self.router.on(event_type, handler)

    def route_event(self, event_type: EnterpriseKnowledgeEventType,
                    payload: dict[str, Any]) -> list[dict[str, Any]]:
        return self.router.route(event_type, payload)

    # -- webhooks ------------------------------------------------------------
    def register_webhook(self, name: str, url: str) -> None:
        self.webhooks.register(name, url)

    def unregister_webhook(self, name: str, url: str | None = None) -> bool:
        return self.webhooks.unregister(name, url)

    def dispatch_event(self, event_type: EnterpriseKnowledgeEventType,
                       payload: dict[str, Any]) -> list[dict[str, Any]]:
        self.route_event(event_type, payload)
        return self.webhooks.dispatch(event_type, payload)

    # -- stats ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "bridge": self.bridge.stats(),
            "webhooks": self.webhooks.stats(),
            "routes": self.router.counts(),
        }
