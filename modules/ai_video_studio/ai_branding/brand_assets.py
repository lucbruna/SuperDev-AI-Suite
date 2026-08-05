"""Brand Assets — real brand asset images (PNG).

Generates palette swatch strips and monogram logo placeholders using PIL,
written under ``modules/downloads/branding/``.
"""
from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_branding.brand_kit import slugify, validate_hex

logger = logging.getLogger(__name__)

_FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/consolab.ttf",
]


def _load_font(size: int):
    """Load a TrueType font, falling back to Pillow's default bitmap font."""
    from PIL import ImageFont

    for candidate in _FONT_CANDIDATES:
        try:
            if os.path.exists(candidate):
                return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_palette_swatches(
    colors: list[str],
    *,
    name: str = "palette",
    size: tuple[int, int] = (640, 80),
    output_path: str | None = None,
) -> dict[str, Any]:
    """Generate a real PNG swatch strip from the brand palette."""
    from PIL import Image, ImageDraw

    started = time.time()
    palette = [validate_hex(color) for color in colors]
    if not palette:
        raise ValidationError("Provide at least one brand color", field="colors")

    width, height = size
    swatch_width = max(width // len(palette), 1)
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for index, color in enumerate(palette):
        left = index * swatch_width
        draw.rectangle([left, 0, min(left + swatch_width, width) - 1, height - 1], fill=color)

    out = Path(output_path) if output_path else unique_filename(
        get_subsystem_dir("branding"), f"swatches_{slugify(name)}", "png"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PNG")
    logger.info("Palette swatches %r written to %s", name, out)
    return {
        "kind": "palette_swatches",
        "name": name,
        "colors": palette,
        "output_path": str(out),
        "output_bytes": out.stat().st_size,
        "width": width,
        "height": height,
        "elapsed_seconds": round(time.time() - started, 3),
    }


def generate_logo_placeholder(
    name: str,
    *,
    color: str = "#FFFFFF",
    background: str = "#1F2937",
    size: tuple[int, int] = (256, 256),
    output_path: str | None = None,
) -> dict[str, Any]:
    """Generate a monogram logo placeholder (first letter on brand color)."""
    from PIL import Image, ImageDraw

    started = time.time()
    if not name or not name.strip():
        raise ValidationError("Brand name is required", field="name")
    foreground = validate_hex(color)
    backdrop = validate_hex(background)
    width, height = size

    image = Image.new("RGB", (width, height), backdrop)
    draw = ImageDraw.Draw(image)
    letter = name.strip()[0].upper()
    font = _load_font(int(width * 0.5))
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2 - bbox[0]
    y = (height - text_height) / 2 - bbox[1]
    draw.text((x, y), letter, fill=foreground, font=font)

    out = Path(output_path) if output_path else unique_filename(
        get_subsystem_dir("branding"), f"logo_{slugify(name)}", "png"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PNG")
    logger.info("Logo placeholder %r written to %s", name, out)
    return {
        "kind": "logo_placeholder",
        "name": name,
        "letter": letter,
        "color": foreground,
        "background": backdrop,
        "output_path": str(out),
        "output_bytes": out.stat().st_size,
        "width": width,
        "height": height,
        "elapsed_seconds": round(time.time() - started, 3),
    }
