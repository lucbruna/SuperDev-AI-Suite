"""Style-specific image generators.

Each generator follows the same interface::

    generator.generate(prompt, *, size=(1024, 1024), model=None, **params)

and returns a structured result dict. The :func:`get_generator` factory
resolves a style name to its generator instance.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_image_generator.generators.realistic_generator import RealisticGenerator
from modules.ai_video_studio.ai_image_generator.generators.anime_generator import AnimeGenerator
from modules.ai_video_studio.ai_image_generator.generators.cinematic_generator import CinematicGenerator
from modules.ai_video_studio.ai_image_generator.generators.fantasy_generator import FantasyGenerator
from modules.ai_video_studio.ai_image_generator.generators.architecture_generator import ArchitectureGenerator
from modules.ai_video_studio.ai_image_generator.generators.agriculture_generator import AgricultureGenerator
from modules.ai_video_studio.ai_image_generator.generators.medical_generator import MedicalGenerator
from modules.ai_video_studio.ai_image_generator.generators.ecommerce_generator import EcommerceGenerator
from modules.ai_video_studio.ai_image_generator.generators.product_generator import ProductGenerator
from modules.ai_video_studio.ai_image_generator.generators.logo_generator import LogoGenerator
from modules.ai_video_studio.ai_image_generator.generators.banner_generator import BannerGenerator
from modules.ai_video_studio.ai_image_generator.generators.thumbnail_generator import ThumbnailGenerator
from modules.ai_video_studio.ai_image_generator.generators.icon_generator import IconGenerator
from modules.ai_video_studio.ai_image_generator.generators.infographic_generator import InfographicGenerator

_GENERATORS: dict[str, Any] = {
    "realistic": RealisticGenerator(),
    "anime": AnimeGenerator(),
    "cinematic": CinematicGenerator(),
    "fantasy": FantasyGenerator(),
    "architecture": ArchitectureGenerator(),
    "agriculture": AgricultureGenerator(),
    "medical": MedicalGenerator(),
    "ecommerce": EcommerceGenerator(),
    "product": ProductGenerator(),
    "logo": LogoGenerator(),
    "banner": BannerGenerator(),
    "thumbnail": ThumbnailGenerator(),
    "icon": IconGenerator(),
    "infographic": InfographicGenerator(),
}

__all__ = [
    "RealisticGenerator",
    "AnimeGenerator",
    "CinematicGenerator",
    "FantasyGenerator",
    "ArchitectureGenerator",
    "AgricultureGenerator",
    "MedicalGenerator",
    "EcommerceGenerator",
    "ProductGenerator",
    "LogoGenerator",
    "BannerGenerator",
    "ThumbnailGenerator",
    "IconGenerator",
    "InfographicGenerator",
    "get_generator",
]


def get_generator(name: str) -> Any:
    """Return the generator instance for a style name."""
    generator = _GENERATORS.get(name)
    if generator is None:
        raise ValueError(f"Unknown generator '{name}'")
    return generator
