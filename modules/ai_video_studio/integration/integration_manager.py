"""Integration manager — boots the studio's real services into the registry.

Consumers can register their own services, subscribe to the event bus, and
inspect the whole integration surface through a single ``status()`` call.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.integration.event_bus import EventBus, get_event_bus
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

        entries: list[tuple[str, Any, str, str]] = [
            ("ai_studio", AIStudioService(), "ai", "AI writing and direction (script, storyboard, plan)"),
            ("voice_studio", VoiceStudioService(), "media", "Text-to-speech synthesis and narrator catalog"),
            ("avatar_engine", AvatarEngine(), "media", "Avatar profiles and generated presenter cards"),
            ("subtitle_studio", SubtitleStudioService(), "media", "SRT generation and subtitle translation"),
            ("export_service", ExportService(), "pipeline", "Multi-format export (mp4/webm/mov/gif)"),
            ("render_engine", RenderEngine(), "pipeline", "FFmpeg-backed rendering and muxing"),
        ]
        for name, instance, kind, description in entries:
            self._registry.register_service(
                name, instance, kind=kind, description=description, version="1.0"
            )
        self._registry.register_module(self.MODULE_NAME)
        self._booted = True
        return self._registry.count()

    def publish(self, event_type: str, **payload: Any) -> int:
        """Synchronous wrapper over the async bus for convenience."""
        import asyncio

        return asyncio.get_event_loop().run_until_complete(
            self._bus.publish(event_type, **payload)
        )

    def status(self) -> dict[str, Any]:
        """Full integration surface for health/ops dashboards."""
        self.register_studio_services()
        by_type: dict[str, int] = {}
        for record in self._bus.history(limit=10_000_000):
            by_type[record["event"]] = by_type.get(record["event"], 0) + 1
        return {
            "module": self.MODULE_NAME,
            "booted": self._booted,
            "services": self._registry.list_services(),
            "service_count": self._registry.count(),
            "modules": self._registry.list_modules(),
            "events": by_type,
            "event_total": sum(by_type.values()),
            "subscribers": self._bus.subscriber_count(),
        }


_manager: IntegrationManager | None = None


def get_integration_manager() -> IntegrationManager:
    """Process-wide singleton manager (boots services on first use)."""
    global _manager
    if _manager is None:
        _manager = IntegrationManager()
    return _manager
