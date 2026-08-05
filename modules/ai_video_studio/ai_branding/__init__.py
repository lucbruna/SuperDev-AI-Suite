"""AI Video Studio — AI Branding Studio (Volume 5).

Brand kits with validated palettes and WCAG contrast analysis, platform SEO
metadata (YouTube/TikTok/Instagram/X/LinkedIn), and brand asset generation
(palette swatches, monogram logos). Real outputs land under
``modules/downloads/branding/`` and ``modules/downloads/seo/``.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_branding.brand_kit import (
    BrandKit,
    build_brand_kit,
    contrast_ratio,
    parse_hex,
    relative_luminance,
    slugify,
    validate_hex,
)
from modules.ai_video_studio.ai_branding.seo_engine import generate_seo_metadata
from modules.ai_video_studio.ai_branding.brand_assets import (
    generate_logo_placeholder,
    generate_palette_swatches,
)

__all__ = [
    "BrandKit",
    "build_brand_kit",
    "contrast_ratio",
    "parse_hex",
    "relative_luminance",
    "slugify",
    "validate_hex",
    "generate_seo_metadata",
    "generate_logo_placeholder",
    "generate_palette_swatches",
]
