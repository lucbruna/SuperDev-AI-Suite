"""Clothing System — wardrobe, garments, materials and textures.

Generators produce per-garment parameters (shirt, pants, jacket, dress,
shoes, hat, glasses, jewelry); the clothing engine assembles full outfits
from fabrics, textures and color palettes.
"""
from modules.ai_video_studio.ai_avatar_engine.clothing.clothing_engine import (
    ClothingEngine,
    get_clothing_engine,
)

__all__ = ["ClothingEngine", "get_clothing_engine"]
