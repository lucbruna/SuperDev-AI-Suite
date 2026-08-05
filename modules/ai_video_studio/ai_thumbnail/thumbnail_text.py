"""Thumbnail text helpers — wrapping, fitting and legibility.

Pure helpers used by the thumbnail engine: word wrapping by character width,
max-line truncation and WCAG contrast enforcement for text colors.
"""
from __future__ import annotations

import logging
from typing import Any

from modules.ai_video_studio.ai_branding.brand_kit import contrast_ratio, relative_luminance, validate_hex

logger = logging.getLogger(__name__)


def wrap_text(text: str, max_chars: int) -> list[str]:
    """Word-wrap text into lines of at most ``max_chars`` characters."""
    if not text:
        return [""]
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            remainder = word
            while len(remainder) > max_chars:
                lines.append(remainder[:max_chars])
                remainder = remainder[max_chars:]
            current = remainder
        elif len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def split_lines(text: str, max_lines: int, max_chars: int = 22) -> list[str]:
    """Wrap text and cap it at ``max_lines`` lines, appending an ellipsis."""
    if max_lines < 1:
        raise ValueError("max_lines must be positive")
    lines = wrap_text(text, max_chars)
    if len(lines) <= max_lines:
        return lines
    head = lines[: max_lines - 1]
    tail = lines[max_lines - 1]
    if len(tail) > 1:
        tail = tail[: max(1, len(tail) - 1)] + "…"
    else:
        tail = "…"
    return head + [tail]


def _mix(foreground: tuple[int, int, int], target: tuple[int, int, int], steps: int) -> tuple[int, int, int]:
    """Interpolate ``foreground`` toward ``target`` by ``steps`` steps."""
    ratio = 1.0 / (steps + 1)
    return (
        round(foreground[0] + (target[0] - foreground[0]) * ratio),
        round(foreground[1] + (target[1] - foreground[1]) * ratio),
        round(foreground[2] + (target[2] - foreground[2]) * ratio),
    )


def ensure_contrast(foreground: str, background: str, min_ratio: float = 4.5) -> str:
    """Return a variant of ``foreground`` with enough contrast on ``background``.

    Interpolates the text color toward white and toward black, keeping the
    side that reaches the target ratio in the fewest steps.
    """
    from modules.ai_video_studio.ai_branding.brand_kit import parse_hex

    if min_ratio < 1:
        raise ValueError("min_ratio must be >= 1")
    current = validate_hex(foreground)
    if contrast_ratio(current, background) >= min_ratio:
        return current

    base = parse_hex(current)
    for steps in range(1, 12):
        for target_name, target in (("white", (255, 255, 255)), ("black", (0, 0, 0))):
            candidate = _mix(base, target, steps)
            candidate_hex = "#{:02x}{:02x}{:02x}".format(*candidate)
            if contrast_ratio(candidate_hex, background) >= min_ratio:
                logger.debug("Adjusted %s -> %s toward %s on %s", current, candidate_hex, target_name, background)
                return candidate_hex
    return "#000000" if relative_luminance(background) < 0.5 else "#ffffff"
