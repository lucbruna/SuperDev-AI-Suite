"""Integration endpoints — registry/event/health surface for ops dashboards."""
from __future__ import annotations
from typing import Any

from fastapi import APIRouter

from modules.ai_video_studio.integration.event_bus import get_event_bus
from modules.ai_video_studio.integration.integration_manager import get_integration_manager

router = APIRouter()


@router.get("/status", tags=["Integration"])
async def integration_status() -> dict[str, Any]:
    """Full integration surface: services, modules, events, subscribers."""
    return get_integration_manager().status()


@router.get("/services", tags=["Integration"])
async def integration_services() -> list[dict[str, Any]]:
    """Registered studio services (registry snapshot)."""
    return get_integration_manager().registry.list_services()


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
