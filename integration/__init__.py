"""Integration & API Engine (Volume 16).

Public API for connecting external systems: connectors and providers, APIs and
gateways, authentication and authorization, webhooks and events, messaging,
transformation, synchronization, marketplace and monitoring.
"""
from __future__ import annotations

# Core engine
from .integration_config import IntegrationConfig
from .integration_engine import IntegrationEngine
from .integration_factory import IntegrationFactory
from .integration_manager import IntegrationManager
from .integration_registry import IntegrationRegistry
from .integration_runtime import IntegrationRuntime

# Subsystem engines (facades over the 12 subpackages)
from .api.api_engine import ApiEngine
from .authentication.auth_engine import AuthEngine
from .authorization.permission_engine import AuthorizationEngine, PermissionEngine
from .connectors.connector_engine import ConnectorEngine
from .events.event_engine import EventEngine
from .gateway.gateway_engine import GatewayEngine
from .marketplace.marketplace_engine import MarketplaceEngine
from .messaging.messaging_engine import MessagingEngine
from .monitoring.monitoring_engine import MonitoringEngine
from .synchronization.sync_engine import SynchronizationEngine
from .transformation.transform_engine import TransformationEngine
from .webhooks.webhook_engine import WebhookEngine

__all__ = [
    "ApiEngine",
    "AuthEngine",
    "AuthorizationEngine",
    "ConnectorEngine",
    "EventEngine",
    "GatewayEngine",
    "IntegrationConfig",
    "IntegrationEngine",
    "IntegrationFactory",
    "IntegrationManager",
    "IntegrationRegistry",
    "IntegrationRuntime",
    "MarketplaceEngine",
    "MessagingEngine",
    "MonitoringEngine",
    "PermissionEngine",
    "SynchronizationEngine",
    "TransformationEngine",
    "WebhookEngine",
]
