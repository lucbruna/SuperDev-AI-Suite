"""YouTube Metadata — title, description and category optimization (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_CATEGORIES = {
    "film": 1,
    "education": 27,
    "entertainment": 24,
    "gaming": 20,
    "music": 10,
    "tech": 28,
    "vlog": 22,
    "howto": 26,
}


class YoutubeMetadata:
    """Assemble YouTube metadata with keyword-driven optimization."""

    def build(
        self,
        *,
        title: str,
        description: str = "",
        keywords: list[str] | None = None,
        category: str = "entertainment",
    ) -> dict:
        """Build a complete metadata bundle for a YouTube upload."""
        category_id = _CATEGORIES.get(category.lower(), 22)
        optimized_title = title[:100]
        tags = (keywords or [])[:15]
        return {
            "title": optimized_title,
            "description": description,
            "tags": tags,
            "category_id": category_id,
            "category": category,
        }

    def optimize_title(self, title: str) -> dict:
        """Score a title for search performance."""
        length = len(title)
        score = 40.0 if 30 <= length <= 65 else 20.0
        if any(c.isdigit() for c in title):
            score += 20.0
        if title.strip().endswith(("?", "!", "…")):
            score += 20.0
        if any(w in title.lower() for w in ["como", "guia", "melhor", "top"]):
            score += 20.0
        return {"title": title, "score": round(min(100.0, score), 1)}

    def stats(self) -> dict[str, int]:
        return {"categories": len(_CATEGORIES)}


_METADATA: YoutubeMetadata | None = None


def get_youtube_metadata() -> YoutubeMetadata:
    """Get the module-level singleton metadata helper."""
    global _METADATA
    if _METADATA is None:
        _METADATA = YoutubeMetadata()
    return _METADATA
