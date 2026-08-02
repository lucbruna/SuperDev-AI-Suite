"""API route modules for AI Video Studio.

All route modules are imported here for convenience. The router
aggregates them via ``api.router.api_router``.
"""
from modules.ai_video_studio.api.routes import (
    project,
    video,
    scene,
    render,
    timeline,
    assets,
    audio,
    subtitles,
)

__all__ = [
    "project",
    "video",
    "scene",
    "render",
    "timeline",
    "assets",
    "audio",
    "subtitles",
]
