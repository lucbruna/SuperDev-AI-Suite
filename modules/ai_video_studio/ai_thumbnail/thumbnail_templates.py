"""Thumbnail templates — reusable visual presets.

Each template defines background, accent, text and outline colors plus a
layout style. Used by the thumbnail engine to render thumbnails.
"""
from __future__ import annotations

import logging
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

THUMBNAIL_TEMPLATES: dict[str, dict[str, Any]] = {
    "bold_title": {
        "background": "#111827",
        "accent": "#F59E0B",
        "text": "#FFFFFF",
        "outline": "#000000",
        "style": "centered",
    },
    "minimal": {
        "background": "#FFFFFF",
        "accent": "#111827",
        "text": "#111827",
        "outline": None,
        "style": "centered",
    },
    "split_frame": {
        "background": "#0F172A",
        "accent": "#3B82F6",
        "text": "#FFFFFF",
        "outline": "#000000",
        "style": "split",
    },
    "emoji_pop": {
        "background": "#7C3AED",
        "accent": "#FCD34D",
        "text": "#FFFFFF",
        "outline": "#000000",
        "style": "centered",
    },
}

_LAYOUT_STYLES = {"centered", "split"}


def get_template(name: str) -> dict[str, Any]:
    """Return a validated copy of the named template."""
    template = THUMBNAIL_TEMPLATES.get(name)
    if template is None:
        raise ValidationError(f"Unknown thumbnail template: {name}", field="template")
    if template["style"] not in _LAYOUT_STYLES:
        raise ValidationError(f"Invalid layout style: {template['style']}", field="template")
    return dict(template)


def list_templates() -> list[str]:
    """Return the available template names."""
    return list(THUMBNAIL_TEMPLATES)
