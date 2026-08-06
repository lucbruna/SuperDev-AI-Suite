"""Publisher endpoints — multi-platform publishing (YouTube, TikTok, etc.).

Exposes the ``PublisherEngine`` (Volume 7) over HTTP: platform discovery,
content publishing, scheduling and status/stats. Engine calls that touch the
queue run via :func:`asyncio.to_thread` so the event loop is never blocked.
"""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from modules.ai_video_studio.ai_publisher.publisher_engine import get_publisher_engine

router = APIRouter()


class PublishRequest(BaseModel):
    content: dict = Field(default_factory=dict, description="Content payload to publish")
    platforms: list[str] = Field(..., min_length=1, description="Target platforms (e.g. youtube, tiktok)")


class ScheduleRequest(BaseModel):
    content: dict = Field(default_factory=dict, description="Content payload to publish")
    platforms: list[str] = Field(..., min_length=1, description="Target platforms")
    schedule_at: float | None = Field(default=None, description="Unix timestamp for scheduled publication")


@router.get("/platforms", summary="List available publishing platforms")
async def list_platforms():
    """Platforms whose client subpackages are installed."""
    return {"platforms": get_publisher_engine().available_platforms()}


@router.post("/publish", summary="Publish content to one or more platforms")
async def publish(req: PublishRequest):
    """Enqueue content for publication on the requested platforms."""
    engine = get_publisher_engine()
    result = await asyncio.to_thread(engine.publish, content=req.content, platforms=req.platforms)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "publish failed"))
    return result


@router.post("/schedule", summary="Schedule content for future publication")
async def schedule(req: ScheduleRequest):
    """Enqueue content for publication at a future time."""
    engine = get_publisher_engine()
    result = await asyncio.to_thread(
        engine.schedule, content=req.content, platforms=req.platforms, schedule_at=req.schedule_at
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "schedule failed"))
    return result


@router.get("/status", summary="Publisher engine status")
async def status():
    """Engine status: started flag, queued jobs, available platforms."""
    return get_publisher_engine().get_status()


@router.get("/stats", summary="Publisher engine statistics")
async def stats():
    """Cumulative publish counters."""
    return get_publisher_engine().stats()
