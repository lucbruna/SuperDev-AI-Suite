"""Main API router aggregating all endpoint modules."""
from __future__ import annotations

from fastapi import APIRouter

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
    publisher,
    render,
    scene,
    skills,
    subtitles,
    studios,
    suite_integration,
    timeline,
    video,
    visual_assets,
)
api_router = APIRouter()

api_router.include_router(ai.router, prefix="/ai", tags=["AI Studio"])
api_router.include_router(video.router, prefix="/videos", tags=["Videos"])
api_router.include_router(visual_assets.router, prefix="/visual-assets", tags=["Visual Assets"])
api_router.include_router(project.router, prefix="/projects", tags=["Projects"])
api_router.include_router(publisher.router, prefix="/publisher", tags=["Publisher"])
api_router.include_router(scene.router, prefix="/scenes", tags=["Scenes"])
api_router.include_router(render.router, prefix="/render", tags=["Render"])
api_router.include_router(timeline.router, prefix="/timelines", tags=["Timelines"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(audio.router, prefix="/audio", tags=["Audio"])
api_router.include_router(avatar.router, prefix="/avatars", tags=["Avatars"])
api_router.include_router(avatar_engine.router, prefix="/avatar-engine", tags=["Avatar Engine (Volume 6)"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])
api_router.include_router(subtitles.router, prefix="/subtitles", tags=["Subtitles"])
api_router.include_router(studios.router, prefix="/studios", tags=["DARKSTUDIO"])
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
async def studio_stats():
    """Return local workspace counters without requiring the legacy SQL backend.

    Project, render and export CRUD routes currently use local process stores.
    Video generation jobs are tracked by the video route module. These counters
    describe the running local API process, not durable database totals.
    """
    active_statuses = {"queued", "processing", "rendering", "running"}
    local_renders = getattr(render, "_renders", {})
    video_jobs = getattr(video, "_jobs", {})
    active_renders = sum(
        1 for item in local_renders.values()
        if str(item.get("status", "")).lower() in active_statuses
    ) + sum(
        1 for item in video_jobs.values()
        if str(item.get("status", "")).lower() in active_statuses
    )
    return {
        "total_projects": len(getattr(project, "_projects", {})),
        "active_renders": active_renders,
        "total_exports": len(getattr(export, "_exports", {})),
        "storage_used_mb": 0.0,
    }
