"""Skill events — publishes skill lifecycle events onto the integration bus."""
from __future__ import annotations
import asyncio
from typing import Any, Coroutine


async def publish(event_type: str, **payload: Any) -> int:
    """Publish a ``skill.*`` event onto the Vol 10 integration event bus (best effort)."""
    try:
        from modules.ai_video_studio.integration.event_bus import get_event_bus

        return await get_event_bus().publish(f"skill.{event_type}", **payload)
    except Exception:  # noqa: BLE001 — skills must never break on a missing bus
        return 0


def fire_sync(coro: Coroutine[Any, Any, Any]) -> None:
    """Fire an event coroutine safely from both sync and async contexts.

    Inside a running loop we schedule fire-and-forget; otherwise we run a
    fresh loop (avoids the Python 3.11+ ``get_event_loop`` RuntimeError).
    """
    try:
        asyncio.get_running_loop().create_task(coro)
    except RuntimeError:
        asyncio.run(coro)


async def skill_installed(skill_id: str, version: str) -> int:
    return await publish("installed", skill_id=skill_id, version=version)


async def skill_updated(skill_id: str, old_version: str, new_version: str) -> int:
    return await publish("updated", skill_id=skill_id, old_version=old_version, new_version=new_version)


async def skill_uninstalled(skill_id: str) -> int:
    return await publish("uninstalled", skill_id=skill_id)


async def skill_executed(
    skill_id: str, ok: bool, duration_ms: float, error: str | None = None
) -> int:
    return await publish(
        "executed", skill_id=skill_id, ok=ok, duration_ms=duration_ms, error=error
    )
