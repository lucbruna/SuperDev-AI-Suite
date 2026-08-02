"""Integration endpoints — registry/event/health surface for ops dashboards."""
from __future__ import annotations
from typing import Any

from fastapi import APIRouter

from modules.ai_video_studio.integration.event_bus import get_event_bus
from modules.ai_video_studio.integration.integration_manager import get_integration_manager

router = APIRouter()


@router.get("/status", tags=["Integration"])
async def integration_status() -> dict[str, Any]:
    """Full integration surface: services, modules, health, stats, events."""
    return get_integration_manager().status()


@router.get("/services", tags=["Integration"])
async def integration_services() -> list[dict[str, Any]]:
    """Registered studio services (registry snapshot)."""
    return get_integration_manager().registry.list_services()


@router.get("/health", tags=["Integration"])
async def integration_health() -> dict[str, Any]:
    """Per-service health snapshot (registration + dependency graph)."""
    return get_integration_manager().health.check_all()


@router.get("/dependencies", tags=["Integration"])
async def integration_dependencies() -> dict[str, Any]:
    """Declared dependency graph with topological resolution order."""
    return get_integration_manager().dependencies.snapshot()


@router.get("/statistics", tags=["Integration"])
async def integration_statistics() -> dict[str, Any]:
    """Usage statistics per service and event-type counts."""
    return get_integration_manager().statistics.stats()


@router.get("/cache", tags=["Integration"])
async def integration_cache() -> dict[str, Any]:
    """Integration cache stats (hits/misses/entries)."""
    return get_integration_manager().cache.stats()


@router.get("/logs", tags=["Integration"])
async def integration_logs(limit: int = 100, level: str | None = None) -> list[dict[str, Any]]:
    """Recent structured integration log entries, newest first."""
    return get_integration_manager().logger.entries(limit=max(1, min(limit, 500)), level=level)


@router.get("/events", tags=["Integration"])
async def integration_events(limit: int = 50) -> list[dict[str, Any]]:
    """Recent event-bus history, newest first."""
    return get_event_bus().history(limit=max(1, min(limit, 500)))


@router.post("/publish", tags=["Integration"])
async def integration_publish(payload: dict[str, Any]) -> dict[str, Any]:
    """Publish a custom event onto the bus (for testing/integration)."""
    payload = dict(payload)
    event_type = str(payload.pop("event", "integration.custom"))
    count = await get_event_bus().publish(event_type, **payload)
    return {"event": event_type, "subscribers_triggered": count}
