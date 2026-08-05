"""Subtitle Formatter — line wrapping and inline markup helpers."""
from __future__ import annotations

from modules.ai_video_studio.ai_subtitles.subtitle_generator import chunk_text


def wrap(text: str, max_chars: int = 42) -> str:
    """Wrap to ``max_chars`` lines joined with newlines (max 2 lines)."""
    lines = chunk_text(text, max_chars)
    if len(lines) > 2:
        # Re-wrap aggressively into two lines.
        words = text.split()
        mid = len(words) // 2
        return f"{' '.join(words[:mid])}\n{' '.join(words[mid:])}"
    return "\n".join(lines)


def strip_markup(text: str) -> str:
    """Remove SRT/VTT/ASS markup from raw text."""
    import re

    return re.sub(r"<[^>]+>|\{[^}]*\}|\\N|\\n", " ", text)


def split_cues(text: str) -> list[str]:
    """Split a cue text on explicit ``|`` separators (up to 2 parts)."""
    parts = [p.strip() for p in text.split("|")]
    return parts[:2] if len(parts) >= 2 else [text]
