"""Integration manager — boots the studio's real services into the registry.

Consumers can register their own services, subscribe to the event bus, and
inspect the whole integration surface through a single ``status()`` call.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.integration.dependency_manager import (
    DependencyManager,
    get_dependency_manager,
)
from modules.ai_video_studio.integration.event_bus import EventBus, get_event_bus
from modules.ai_video_studio.integration.health_monitor import (
    HealthMonitor,
    get_health_monitor,
)
from modules.ai_video_studio.integration.integration_cache import (
    IntegrationCache,
    get_integration_cache,
)
from modules.ai_video_studio.integration.integration_logger import (
    IntegrationLogger,
    get_integration_logger,
)
from modules.ai_video_studio.integration.integration_statistics import (
    IntegrationStatistics,
    get_integration_statistics,
)
from modules.ai_video_studio.integration.module_registry import ModuleRegistry, get_registry
from modules.ai_video_studio.integration.service_locator import ServiceLocator, get_service_locator


class IntegrationManager:
    """Orchestrates registration, event flow and health introspection."""

    MODULE_NAME = "ai_video_studio"

    def __init__(
        self,
        registry: ModuleRegistry | None = None,
        bus: EventBus | None = None,
        locator: ServiceLocator | None = None,
    ) -> None:
        self._registry = registry or get_registry()
        self._bus = bus or get_event_bus()
        self._locator = locator or get_service_locator()
        self._booted = False

    @property
    def registry(self) -> ModuleRegistry:
        return self._registry

    @property
    def bus(self) -> EventBus:
        return self._bus

    @property
    def locator(self) -> ServiceLocator:
        return self._locator

    @property
    def dependencies(self) -> DependencyManager:
        return get_dependency_manager()

    @property
    def health(self) -> HealthMonitor:
        return get_health_monitor()

    @property
    def cache(self) -> IntegrationCache:
        return get_integration_cache()

    @property
    def statistics(self) -> IntegrationStatistics:
        return get_integration_statistics()

    @property
    def logger(self) -> IntegrationLogger:
        return get_integration_logger()

    def register_studio_services(self) -> int:
        """Register the studio's real service instances (idempotent)."""
        if self._booted:
            return self._registry.count()

        # Lazy imports keep package import cycle-free.
        from modules.ai_video_studio.render_engine import RenderEngine
        from modules.ai_video_studio.services.ai_studio import AIStudioService
        from modules.ai_video_studio.services.avatar_engine import AvatarEngine
        from modules.ai_video_studio.services.export_service import ExportService
        from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService
        from modules.ai_video_studio.services.voice_studio import VoiceStudioService
        from modules.ai_video_studio.suite_integration import get_suite_bridge

        entries: list[tuple[str, Any, str, str]] = [
            ("ai_studio", AIStudioService(), "ai", "AI writing and direction (script, storyboard, plan)"),
            ("voice_studio", VoiceStudioService(), "media", "Text-to-speech synthesis and narrator catalog"),
            ("avatar_engine", AvatarEngine(), "media", "Avatar profiles and generated presenter cards"),
            ("subtitle_studio", SubtitleStudioService(), "media", "SRT generation and subtitle translation"),
            ("export_service", ExportService(), "pipeline", "Multi-format export (mp4/webm/mov/gif)"),
            ("render_engine", RenderEngine(), "pipeline", "FFmpeg-backed rendering and muxing"),
            ("suite_bridge", get_suite_bridge(), "platform", "SuperDev suite bridge (auth/security/observability/workflow/integration)"),
        ]
        for name, instance, kind, description in entries:
            self._registry.register_service(
                name, instance, kind=kind, description=description, version="1.0"
            )
        # Declare real dependencies between the booted services.
        self.dependencies.declare("export_service", ["render_engine"])
        self.dependencies.declare("subtitle_studio", ["ai_studio"])
        self.dependencies.declare("voice_studio", ["ai_studio"])
        self._registry.register_module(self.MODULE_NAME)
        self._booted = True
        self.logger.log("integration_manager", f"booted {len(entries)} studio services", level="info")
        return self._registry.count()

    def publish(self, event_type: str, **payload: Any) -> int:
        """Synchronous wrapper over the async bus for convenience."""
        import asyncio

        return asyncio.get_event_loop().run_until_complete(
            self._bus.publish(event_type, **payload)
        )

    def register_connectors(self) -> int:
        """Register the Volume 10 domain connectors (lazy, idempotent)."""
        from modules.ai_video_studio.integration.connectors_registry import get_connectors

        connectors = get_connectors()
        for domain, connector in connectors.items():
            if connector is None:
                continue
            self._registry.register_service(
                f"connector.{domain}",
                connector,
                kind="connector",
                description=connector.description,
                version="1.0",
                tags=["volume10", domain],
            )
        self._registry.register_module("connectors")
        return self._registry.count()

    def list_connectors(self) -> list[dict[str, Any]]:
        """Registered connector service records."""
        return [
            s for s in self._registry.list_services() if s.get("kind") == "connector"
        ]

    def status(self) -> dict[str, Any]:
        """Full integration surface for health/ops dashboards."""
        self.register_studio_services()
        self.register_connectors()
        by_type: dict[str, int] = {}
        for record in self._bus.history(limit=10_000_000):
            by_type[record["event"]] = by_type.get(record["event"], 0) + 1
        health = self.health.check_all()
        return {
            "module": self.MODULE_NAME,
            "booted": self._booted,
            "services": self._registry.list_services(),
            "service_count": self._registry.count(),
            "modules": self._registry.list_modules(),
            "dependencies": self.dependencies.snapshot(),
            "health": health,
            "events": by_type,
            "event_total": sum(by_type.values()),
            "subscribers": self._bus.subscriber_count(),
            "statistics": self.statistics.stats(),
            "cache": self.cache.stats(),
            "logs": self.logger.stats(),
        }


_manager: IntegrationManager | None = None


def get_integration_manager() -> IntegrationManager:
    """Process-wide singleton manager (boots services on first use)."""
    global _manager
    if _manager is None:
        _manager = IntegrationManager()
    return _manager
