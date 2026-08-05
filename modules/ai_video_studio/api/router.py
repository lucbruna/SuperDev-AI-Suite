"""Main API router aggregating all endpoint modules."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai_video_studio.api.routes import (
    admin,
    ai,
    analytics,
    assets,
    audio,
    avatar,
    avatar_engine,
    collaboration,
    export,
    generation,
    integration,
    marketing,
    marketplace,
    project,
    render,
    scene,
    skills,
    subtitles,
    suite_integration,
    timeline,
    video,
)
from modules.ai_video_studio.database.database import get_db
from modules.ai_video_studio.database.models import ExportHistory, RenderJob, VideoProject

api_router = APIRouter()

api_router.include_router(ai.router, prefix="/ai", tags=["AI Studio"])
api_router.include_router(video.router, prefix="/videos", tags=["Videos"])
api_router.include_router(project.router, prefix="/projects", tags=["Projects"])
api_router.include_router(scene.router, prefix="/scenes", tags=["Scenes"])
api_router.include_router(render.router, prefix="/render", tags=["Render"])
api_router.include_router(timeline.router, prefix="/timelines", tags=["Timelines"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(audio.router, prefix="/audio", tags=["Audio"])
api_router.include_router(avatar.router, prefix="/avatars", tags=["Avatars"])
api_router.include_router(avatar_engine.router, prefix="/avatar-engine", tags=["Avatar Engine (Volume 6)"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])
api_router.include_router(subtitles.router, prefix="/subtitles", tags=["Subtitles"])
api_router.include_router(integration.router, prefix="/integration", tags=["Integration"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(generation.router, prefix="", tags=["Generation"])
api_router.include_router(
    suite_integration.router, prefix="/suite-integration", tags=["Suite Integration (Volume 10)"]
)
api_router.include_router(marketplace.router, prefix="/marketplace", tags=["Marketplace"])
api_router.include_router(marketing.branding_router, prefix="/branding", tags=["Branding (Volume 5)"])
api_router.include_router(marketing.marketing_router, prefix="/marketing", tags=["Marketing (Volume 5)"])
api_router.include_router(marketing.thumbnails_router, prefix="/thumbnails", tags=["Thumbnails (Volume 5)"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["Collaboration"])


@api_router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "ai-video-studio", "version": "1.0.0"}


@api_router.get("/stats", tags=["Stats"])
async def studio_stats(db: AsyncSession = Depends(get_db)):
    """Aggregate statistics from the shared database."""
    total_projects = await db.scalar(select(func.count()).select_from(VideoProject))
    active_renders = await db.scalar(
        select(func.count())
        .select_from(RenderJob)
        .where(RenderJob.status.notin_(["completed", "failed", "cancelled"]))
    )
    total_exports = await db.scalar(select(func.count()).select_from(ExportHistory))
    return {
        "total_projects": total_projects or 0,
        "active_renders": active_renders or 0,
        "total_exports": total_exports or 0,
        "storage_used_mb": 0.0,
    }
