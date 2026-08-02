"""Integration statistics — usage counters for services and event types."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class ServiceStats:
    calls: int = 0
    errors: int = 0
    total_ms: float = 0.0
    last_used_at: str | None = None


class IntegrationStatistics:
    """Tracks per-service usage and per-event-type counts via the event bus."""

    def __init__(self, bus=None) -> None:  # type: ignore[no-untyped-def]
        from modules.ai_video_studio.integration.event_bus import get_event_bus

        self._bus = bus or get_event_bus()
        self._services: dict[str, ServiceStats] = {}
        self._event_counts: dict[str, int] = {}
        self._bus.subscribe("integration.service.used", self._on_service_used)
        self._bus.subscribe("*", self._on_any_event)

    async def _on_service_used(self, event_type: str, payload: dict[str, Any]) -> None:
        name = str(payload.get("name", "unknown"))
        stats = self._services.setdefault(name, ServiceStats())
        stats.calls += 1
        if not payload.get("ok", True):
            stats.errors += 1
        stats.total_ms += float(payload.get("duration_ms", 0.0))
        stats.last_used_at = datetime.now(UTC).isoformat()

    async def _on_any_event(self, event_type: str, payload: dict[str, Any]) -> None:
        if event_type == "integration.service.used":
            return  # already counted above
        self._event_counts[event_type] = self._event_counts.get(event_type, 0) + 1

    def record(self, name: str, *, ok: bool = True, duration_ms: float = 0.0) -> None:
        """Manually record a service call (synchronous convenience)."""
        stats = self._services.setdefault(name, ServiceStats())
        stats.calls += 1
        if not ok:
            stats.errors += 1
        stats.total_ms += duration_ms
        stats.last_used_at = datetime.now(UTC).isoformat()

    def stats(self) -> dict[str, Any]:
        return {
            "services": {
                name: {
                    "calls": s.calls,
                    "errors": s.errors,
                    "total_ms": round(s.total_ms, 3),
                    "last_used_at": s.last_used_at,
                }
                for name, s in sorted(self._services.items())
            },
            "events": dict(sorted(self._event_counts.items())),
            "event_total": sum(self._event_counts.values()),
            "service_total": sum(s.calls for s in self._services.values()),
            "reported_at": datetime.now(UTC).isoformat(),
        }


_statistics: IntegrationStatistics | None = None


def get_integration_statistics() -> IntegrationStatistics:
    """Process-wide singleton statistics collector."""
    global _statistics
    if _statistics is None:
        _statistics = IntegrationStatistics()
    return _statistics
