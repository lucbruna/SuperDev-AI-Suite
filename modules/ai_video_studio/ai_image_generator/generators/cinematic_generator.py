"""Cinematic generator — film-like images rendered to real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

CinematicGenerator = make_generator("cinematic", (1024, 576), "cinematic_v2")
