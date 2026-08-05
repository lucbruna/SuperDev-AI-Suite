"""AI Video Studio — AI Thumbnail Studio (Volume 5).

Thumbnail generation with named templates (bold title, minimal, split frame,
emoji pop), auto-sized legible text, and WCAG contrast helpers. Real outputs
land under ``modules/downloads/thumbnails/``.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_thumbnail.thumbnail_engine import ThumbnailEngine, get_thumbnail_engine
from modules.ai_video_studio.ai_thumbnail.thumbnail_templates import THUMBNAIL_TEMPLATES, get_template, list_templates
from modules.ai_video_studio.ai_thumbnail.thumbnail_text import ensure_contrast, split_lines, wrap_text

__all__ = [
    "ThumbnailEngine",
    "get_thumbnail_engine",
    "THUMBNAIL_TEMPLATES",
    "get_template",
    "list_templates",
    "ensure_contrast",
    "split_lines",
    "wrap_text",
]
