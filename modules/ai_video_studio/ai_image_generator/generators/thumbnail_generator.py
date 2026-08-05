"""Thumbnail generator — video thumbnails as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

ThumbnailGenerator = make_generator("thumbnail", (1280, 720), "thumbnail_ctr")
