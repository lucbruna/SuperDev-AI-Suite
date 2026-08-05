"""Realistic generator — photorealistic images rendered to real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

RealisticGenerator = make_generator("realistic", (1024, 1024), "stable_diffusion_xl")
