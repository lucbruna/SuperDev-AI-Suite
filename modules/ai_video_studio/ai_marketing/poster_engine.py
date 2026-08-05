"""Poster Engine — real promo poster images (PNG).

Renders a promotional poster (background, title, subtitle and CTA banner)
using PIL, written under ``modules/downloads/marketing/``.
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
]


def _load_font(size: int):
    from PIL import ImageFont

    for candidate in _FONT_CANDIDATES:
        try:
            if os.path.exists(candidate):
                return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            lines.append(word[:max_chars])
        elif len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def generate_poster(
    title: str,
    *,
    subtitle: str | None = None,
    cta: str | None = None,
    colors: tuple[str, str] = ("#111827", "#F59E0B"),
    size: tuple[int, int] = (1080, 1080),
    output_path: str | None = None,
) -> dict[str, Any]:
    """Generate a promotional poster PNG with title, subtitle and CTA banner."""
    from PIL import Image, ImageDraw

    started = time.time()
    if not title or not title.strip():
        raise ValidationError("Poster title is required", field="title")
    background = validate_hex(colors[0])
    accent = validate_hex(colors[1] if len(colors) > 1 else colors[0])
    width, height = size

    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)

    # Diagonal accent corner + baseline stripe.
    draw.polygon([(0, height), (int(width * 0.45), 0), (int(width * 0.65), 0), (0, height)], fill=accent)
    draw.rectangle([0, height - 14, width, height], fill=accent)

    title_font = _load_font(max(width // 12, 16))
    lines = _wrap_text(title.strip(), 16)
    sample = draw.textbbox((0, 0), "Ag", font=title_font)
    line_height = max(sample[3] - sample[1] + 12, 28)
    total = len(lines) * line_height
    y = max(int(height * 0.30), 40)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = bbox[2] - bbox[0]
        draw.text(((width - line_width) / 2 - bbox[0], y - bbox[1]), line, fill="#FFFFFF", font=title_font)
        y += line_height

    if subtitle:
        sub_font = _load_font(max(width // 20, 12))
        sub_bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sub_width = sub_bbox[2] - sub_bbox[0]
        draw.text(
            ((width - sub_width) / 2 - sub_bbox[0], y - sub_bbox[1]),
            subtitle, fill="#E5E7EB", font=sub_font,
        )

    if cta:
        cta_font = _load_font(max(width // 22, 12))
        cta_bbox = draw.textbbox((0, 0), cta, font=cta_font)
        cta_width = cta_bbox[2] - cta_bbox[0]
        banner_y = height - 90
        draw.rounded_rectangle(
            [(width - cta_width - 80) / 2, banner_y, (width + cta_width + 80) / 2, banner_y + 60],
            radius=30, fill=accent,
        )
        draw.text(
            ((width - cta_width) / 2 - cta_bbox[0], banner_y + 30 - (cta_bbox[3] - cta_bbox[1]) / 2 - cta_bbox[1]),
            cta, fill="#111827", font=cta_font,
        )

    out = Path(output_path) if output_path else unique_filename(
        get_subsystem_dir("marketing"), f"poster_{slugify(title)}", "png"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, format="PNG")
    logger.info("Poster %r written to %s", title, out)
    return {
        "kind": "poster",
        "title": title,
        "output_path": str(out),
        "output_bytes": out.stat().st_size,
        "width": width,
        "height": height,
        "background": background,
        "accent": accent,
        "elapsed_seconds": round(time.time() - started, 3),
    }
