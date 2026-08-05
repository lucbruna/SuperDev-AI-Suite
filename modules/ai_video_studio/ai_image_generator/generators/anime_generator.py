"""Anime generator — anime style images rendered to real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

AnimeGenerator = make_generator("anime", (1024, 1024), "anything_v5")
