"""Thumbnail Engine — real thumbnail images (PNG).

Renders YouTube-style thumbnails from a title: template background, accent
graphics, wrapped and auto-sized title text with outline for legibility, and
an optional subtitle. Files land under ``modules/downloads/thumbnails/``.
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
from modules.ai_video_studio.ai_thumbnail.thumbnail_templates import get_template
from modules.ai_video_studio.ai_thumbnail.thumbnail_text import split_lines

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


class ThumbnailEngine:
    """Renders thumbnail PNGs from titles using named templates."""

    def generate(
        self,
        title: str,
        *,
        template: str = "bold_title",
        size: tuple[int, int] = (1280, 720),
        subtitle: str | None = None,
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Generate a thumbnail PNG; returns ``{output_path, size, ...}``."""
        from PIL import Image, ImageDraw

        started = time.time()
        if not title or not title.strip():
            raise ValidationError("Thumbnail title is required", field="title")
        spec = get_template(template)
        width, height = size
        if width < 320 or height < 180:
            raise ValidationError(f"Thumbnail size too small: {size}", field="size")

        background = validate_hex(spec["background"])
        accent = validate_hex(spec["accent"])
        text_color = validate_hex(spec["text"])
        outline = spec["outline"]

        image = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(image)

        # Template graphics.
        if spec["style"] == "split":
            draw.polygon(
                [(0, height), (int(width * 0.42), 0), (int(width * 0.62), 0), (0, height)],
                fill=accent,
            )
        else:
            draw.rectangle([0, height - 18, width, height], fill=accent)

        # Auto-sized title: start large and shrink until it fits.
        lines = split_lines(title.strip(), max_lines=3)
        size_px = width // 7
        min_size = max(width // 32, 14)
        font = _load_font(size_px)
        while size_px > min_size:
            widest = max(draw.textlength(line, font=font) for line in lines)
            if widest <= width * 0.92:
                break
            size_px -= 4
            font = _load_font(size_px)

        sample = draw.textbbox((0, 0), "Ag", font=font)
        line_height = sample[3] - sample[1] + 14
        total_height = len(lines) * line_height
        y = (height - total_height) / 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (width - (bbox[2] - bbox[0])) / 2 - bbox[0]
            if outline:
                for offset in (-3, 3):
                    draw.text((x + offset, y + offset), line, fill=outline, font=font)
            draw.text((x, y), line, fill=text_color, font=font)
            y += line_height

        # Subtitle below the title in the accent color.
        if subtitle:
            sub_font = _load_font(max(width // 22, 12))
            sub_bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
            sub_width = sub_bbox[2] - sub_bbox[0]
            draw.text(
                ((width - sub_width) / 2 - sub_bbox[0], y + 8 - sub_bbox[1]),
                subtitle, fill=accent, font=sub_font,
            )

        out = Path(output_path) if output_path else unique_filename(
            get_subsystem_dir("thumbnails"), f"thumb_{slugify(title)}", "png"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        image.save(out, format="PNG")
        logger.info("Thumbnail %r written to %s", title, out)
        return {
            "kind": "thumbnail",
            "title": title,
            "template": template,
            "style": spec["style"],
            "output_path": str(out),
            "output_bytes": out.stat().st_size,
            "width": width,
            "height": height,
            "elapsed_seconds": round(time.time() - started, 3),
        }


_THUMBNAIL_ENGINE: ThumbnailEngine | None = None


def get_thumbnail_engine() -> ThumbnailEngine:
    """Return the shared ThumbnailEngine singleton."""
    global _THUMBNAIL_ENGINE
    if _THUMBNAIL_ENGINE is None:
        _THUMBNAIL_ENGINE = ThumbnailEngine()
    return _THUMBNAIL_ENGINE
