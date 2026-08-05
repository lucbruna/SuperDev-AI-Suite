"""Hairstyle Studio — hairstyle catalogs and color engine.

Style modules (short, medium, long, curly, straight, afro, beard,
mustache, eyebrows) each expose a list of style descriptors; the
``HairstyleEngine`` selects styles and the ``color_engine`` applies colors.
"""
from modules.ai_video_studio.ai_avatar_engine.hairstyles.hairstyle_engine import (
    HairstyleEngine,
    get_hairstyle_engine,
)

__all__ = ["HairstyleEngine", "get_hairstyle_engine"]
