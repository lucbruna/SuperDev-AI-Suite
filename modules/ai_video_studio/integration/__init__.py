"""Integration package — blueprint Volume 10 core.

Self-contained glue that lets the studio talk to itself and to the platform
without duplicating wiring: a service registry, an async event bus, a
service locator, and an integration manager that boots the studio's real
services. Business-module connectors (Agriculture/ERP/CRM/...) are out of
scope here — they live in their own modules and consume this core.
"""
from __future__ import annotations

from modules.ai_video_studio.integration.event_bus import EventBus, get_event_bus
from modules.ai_video_studio.integration.integration_manager import IntegrationManager
from modules.ai_video_studio.integration.module_registry import ModuleRegistry, get_registry
from modules.ai_video_studio.integration.service_locator import ServiceLocator

__all__ = [
    "EventBus",
    "get_event_bus",
    "IntegrationManager",
    "ModuleRegistry",
    "get_registry",
    "ServiceLocator",
]
