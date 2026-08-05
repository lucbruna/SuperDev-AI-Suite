"""FastAPI application factory for AI Video Studio."""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.ai_video_studio.core.settings import get_settings
from modules.ai_video_studio.core.version import __version__
from modules.ai_video_studio.api.router import api_router
from modules.ai_video_studio.skills.bundles import register_all_concrete
from modules.ai_video_studio.skills.skill_engine import get_skill_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    settings = get_settings()
    settings.storage.ensure_dirs()
    # Register the shipped skill catalog so the API serves it out of the box.
    register_all_concrete(get_skill_engine())
    yield
    # Shutdown: nothing persistent to close for in-process renderers


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="AI Video Studio",
        description="Enterprise video production platform with AI-powered generation, editing, and publishing.",
        version=__version__,
        docs_url="/api/v1/video-studio/docs",
        redoc_url="/api/v1/video-studio/redoc",
        openapi_url="/api/v1/video-studio/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1/video-studio")
    return app
