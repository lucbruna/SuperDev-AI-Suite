"""Integration: API bridge, event routing, REST client and webhooks."""

from __future__ import annotations

from enterprise_knowledge.integration.api_bridge import ApiBridge
from enterprise_knowledge.integration.event_router import EventRouter
from enterprise_knowledge.integration.integration_engine import IntegrationEngine
from enterprise_knowledge.integration.rest_client import RestClient
from enterprise_knowledge.integration.webhook_dispatcher import WebhookDispatcher

__all__ = [
    "ApiBridge",
    "EventRouter",
    "IntegrationEngine",
    "RestClient",
    "WebhookDispatcher",
]
