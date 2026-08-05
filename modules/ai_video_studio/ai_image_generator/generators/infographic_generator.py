"""Infographic generator — data visual designs as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

InfographicGenerator = make_generator("infographic", (1080, 1920), "infographic_designer")
