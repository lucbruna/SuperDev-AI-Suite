"""Fantasy generator — fantasy artwork rendered to real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

FantasyGenerator = make_generator("fantasy", (1024, 1024), "fantasy_art")
