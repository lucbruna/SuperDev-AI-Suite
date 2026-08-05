"""Icon generator — UI icons as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

IconGenerator = make_generator("icon", (512, 512), "icon_flat")
