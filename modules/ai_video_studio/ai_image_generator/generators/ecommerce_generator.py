"""Ecommerce generator — storefront imagery as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

EcommerceGenerator = make_generator("ecommerce", (1024, 1024), "ecommerce_xl")
