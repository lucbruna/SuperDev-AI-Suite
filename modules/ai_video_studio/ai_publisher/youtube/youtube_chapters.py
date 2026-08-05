"""YouTube Chapters — auto-generates chapter timestamps from scene data (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class YoutubeChapters:
    """Build chapter markers from scene timestamps and titles."""

    @staticmethod
    def from_scenes(scenes: list[dict]) -> dict:
        """Convert scene descriptors into YouTube chapter format.

        Each scene: {"start": float (seconds), "title": str}
        """
        chapters = []
        for scene in scenes:
            start = float(scene.get("start", 0))
            title = scene.get("title") or scene.get("label") or f"Chapter {len(chapters) + 1}"
            minutes = int(start // 60)
            seconds = int(start % 60)
            chapters.append({"timestamp": f"{minutes:02d}:{seconds:02d}", "title": title})
        text = "\n".join(f"{c['timestamp']} {c['title']}" for c in chapters)
        return {"chapters": chapters, "description_text": text, "count": len(chapters)}

    @staticmethod
    def validate(timestamps: list[str]) -> dict:
        """Validate a list of MM:SS timestamp strings."""
        valid, invalid = [], []
        for ts in timestamps:
            parts = ts.split(":")
            ok = len(parts) == 2 and all(p.isdigit() for p in parts)
            (valid if ok else invalid).append(ts)
        return {"valid": valid, "invalid": invalid, "count": len(valid)}

    def stats(self) -> dict[str, int]:
        return {"max_chapters": 100}


_CHAPTERS: YoutubeChapters | None = None


def get_youtube_chapters() -> YoutubeChapters:
    """Get the module-level singleton chapters helper."""
    global _CHAPTERS
    if _CHAPTERS is None:
        _CHAPTERS = YoutubeChapters()
    return _CHAPTERS
