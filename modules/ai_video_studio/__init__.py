"""AI Video Studio — Enterprise video production platform.

Core modules:
  - core: Constants, settings, exceptions, paths, feature flags
  - database: SQLAlchemy models and async session management
  - api: FastAPI routes with CRUD endpoints
  - services: Business logic layer
  - render_engine: FFmpeg-based video rendering
  - pipelines: Video generation pipelines (text-to-video, etc.)

Volume 2 — AI planning engines:
  - ai_timeline: Editing timeline, tracks, layers, transitions, playback
  - ai_prompt_engine: Prompt processing, classification, rewriting, optimization
  - ai_scene_planner: Scene/shot/location/character/lighting planning
  - ai_storyboard: Storyboard frames, layouts, timeline, preview
  - ai_screenwriter: Script generation, prompts, review, exports
  - ai_director: Production planning, shooting plan, decisions, learning, analytics
"""
from modules.ai_video_studio.core.version import __version__

__all__ = ["__version__"]
