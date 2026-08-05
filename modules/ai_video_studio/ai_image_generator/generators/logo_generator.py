"""Logo generator — logo concepts as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

LogoGenerator = make_generator("logo", (1024, 1024), "logo_sd")
