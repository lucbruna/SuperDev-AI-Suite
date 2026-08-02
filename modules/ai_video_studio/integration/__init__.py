"""Integration package — blueprint Volume 10 core.

Self-contained glue that lets the studio talk to itself and to the platform
without duplicating wiring: a service registry, an async event bus, a
service locator, a dependency manager, a health monitor, a TTL cache,
usage statistics, a structured logger, and an integration manager that
boots the studio's real services. Business-module connectors
(Agriculture/ERP/CRM/...) live in their own modules and consume this core.
"""
from __future__ import annotations

from modules.ai_video_studio.integration.dependency_manager import (
    DependencyError,
    DependencyManager,
    get_dependency_manager,
)
from modules.ai_video_studio.integration.event_bus import EventBus, get_event_bus
from modules.ai_video_studio.integration.health_monitor import HealthMonitor, get_health_monitor
from modules.ai_video_studio.integration.integration_cache import (
    IntegrationCache,
    get_integration_cache,
)
from modules.ai_video_studio.integration.integration_logger import (
    IntegrationLogger,
    get_integration_logger,
)
from modules.ai_video_studio.integration.integration_manager import (
    IntegrationManager,
    get_integration_manager,
)
from modules.ai_video_studio.integration.integration_statistics import (
    IntegrationStatistics,
    get_integration_statistics,
)
from modules.ai_video_studio.integration.module_registry import ModuleRegistry, get_registry
from modules.ai_video_studio.integration.service_locator import (
    ServiceLocator,
    ServiceNotFoundError,
    get_service_locator,
)

__all__ = [
    "DependencyError",
    "DependencyManager",
    "get_dependency_manager",
    "EventBus",
    "get_event_bus",
    "HealthMonitor",
    "get_health_monitor",
    "IntegrationCache",
    "get_integration_cache",
    "IntegrationLogger",
    "get_integration_logger",
    "IntegrationManager",
    "get_integration_manager",
    "IntegrationStatistics",
    "get_integration_statistics",
    "ModuleRegistry",
    "get_registry",
    "ServiceLocator",
    "ServiceNotFoundError",
    "get_service_locator",
]
