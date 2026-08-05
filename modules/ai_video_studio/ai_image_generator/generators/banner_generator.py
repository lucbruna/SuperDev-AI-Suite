"""Banner generator — web banner imagery as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

BannerGenerator = make_generator("banner", (1920, 1080), "banner_gen")
