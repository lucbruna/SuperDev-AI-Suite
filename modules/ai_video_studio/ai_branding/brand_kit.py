"""Brand Kit — real brand kit documents (JSON).

Builds a structured brand kit from name, colors, tone and fonts, validates
the palette (hex format + WCAG contrast pairs) and writes a real JSON file
under ``modules/downloads/branding/``.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename

logger = logging.getLogger(__name__)

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")

_TONES = {"professional", "playful", "luxury", "bold", "minimal"}

_DEFAULT_FONTS = ["Inter", "Montserrat"]


def slugify(text: str) -> str:
    """Normalize arbitrary text into a filesystem-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if not slug:
        raise ValidationError("Cannot build a slug from empty text", field="name")
    return slug


def validate_hex(color: str) -> str:
    """Validate a ``#RRGGBB`` hex color, normalizing to lowercase."""
    if not isinstance(color, str) or not _HEX_RE.match(color):
        raise ValidationError(f"Invalid hex color: {color!r}", field="colors")
    return color.lower()


def parse_hex(color: str) -> tuple[int, int, int]:
    """Return (r, g, b) ints from a validated hex color."""
    c = validate_hex(color).lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _linearize(channel: int) -> float:
    value = channel / 255.0
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(color: str) -> float:
    """WCAG relative luminance for a hex color."""
    r, g, b = parse_hex(color)
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def contrast_ratio(foreground: str, background: str) -> float:
    """WCAG contrast ratio between two hex colors (1.0 to 21.0)."""
    l1 = relative_luminance(foreground)
    l2 = relative_luminance(background)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


@dataclass
class BrandKit:
    """Structured brand identity document."""

    name: str
    colors: list[str]
    tagline: str = ""
    tone: str = "professional"
    fonts: list[str] = field(default_factory=lambda: list(_DEFAULT_FONTS))


def _contrast_pairs(colors: list[str]) -> dict[str, float]:
    """Accessibility contrast for every ordered color pair."""
    pairs: dict[str, float] = {}
    for foreground in colors:
        for background in colors:
            if foreground == background:
                continue
            pairs[f"{foreground}_on_{background}"] = round(contrast_ratio(foreground, background), 2)
    return pairs


def build_brand_kit(
    name: str,
    *,
    colors: list[str],
    tagline: str = "",
    tone: str = "professional",
    fonts: list[str] | None = None,
    output_path: str | None = None,
) -> dict[str, Any]:
    """Build a brand kit document and write it as JSON.

    Returns ``{name, colors, tone, contrast, output_path, ...}``.
    """
    if not name or not name.strip():
        raise ValidationError("Brand name is required", field="name")
    if len(colors) < 2:
        raise ValidationError("Provide at least two brand colors", field="colors")
    if tone not in _TONES:
        raise ValidationError(f"Unknown tone: {tone}", field="tone")

    palette = [validate_hex(color) for color in colors]
    kit = BrandKit(name=name.strip(), colors=palette, tagline=tagline.strip(), tone=tone,
                   fonts=fonts or list(_DEFAULT_FONTS))

    data = asdict(kit)
    data["created_at"] = datetime.now(timezone.utc).isoformat()
    data["contrast"] = _contrast_pairs(palette)

    out_dir = Path(output_path).parent if output_path else get_subsystem_dir("branding")
    out_path = Path(output_path) if output_path else unique_filename(out_dir, f"brandkit_{slugify(name)}", "json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    data["output_path"] = str(out_path)
    data["output_bytes"] = out_path.stat().st_size
    logger.info("Brand kit %r written to %s", name, out_path)
    return data
