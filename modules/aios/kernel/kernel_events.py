"""Kernel events — publishes ``kernel.*`` events onto the Vol 10 bus."""
from __future__ import annotations
from typing import Any


async def emit(event_type: str, **payload: Any) -> int:
    """Publish a ``kernel.*`` event on the integration event bus (best effort)."""
    try:
        from modules.ai_video_studio.integration.event_bus import get_event_bus

        return await get_event_bus().publish(f"kernel.{event_type}", **payload)
    except Exception:  # noqa: BLE001 — kernel must never break on a missing bus
        return 0
