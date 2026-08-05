"""Product generator — product shots as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

ProductGenerator = make_generator("product", (1024, 1024), "product_photography")
