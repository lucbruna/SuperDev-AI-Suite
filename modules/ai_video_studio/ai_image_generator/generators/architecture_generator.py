"""Architecture generator — architectural renders as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

ArchitectureGenerator = make_generator("architecture", (1280, 720), "architecture_sd")
