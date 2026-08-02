"""AI Video Studio — Enterprise video production platform.

Core modules:
  - core: Constants, settings, exceptions, paths, feature flags
  - database: SQLAlchemy models and async session management
  - api: FastAPI routes with CRUD endpoints
  - services: Business logic layer
  - render_engine: FFmpeg-based video rendering
  - pipelines: Video generation pipelines (text-to-video, etc.)
"""
from modules.ai_video_studio.core.version import __version__

__all__ = ["__version__"]
