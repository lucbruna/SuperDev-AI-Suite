"""YouTube SEO — search optimization for YouTube videos (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class YoutubeSeo:
    """Score video SEO readiness and generate keyword suggestions."""

    def score(
        self,
        *,
        title: str = "",
        description: str = "",
        tags: list[str] | None = None,
        has_transcript: bool = False,
        has_thumbnail: bool = False,
    ) -> dict:
        """Return an SEO readiness score (0-100) with breakdown."""
        tags = tags or []
        score = 0.0
        breakdown = {}
        score += 30.0 if 30 <= len(title) <= 65 else 10.0
        breakdown["title"] = "good" if 30 <= len(title) <= 65 else "needs_work"
        score += 25.0 if len(description.split()) >= 50 else 10.0
        breakdown["description"] = "good" if len(description.split()) >= 50 else "needs_work"
        score += 25.0 if len(tags) >= 5 else 10.0
        breakdown["tags"] = "good" if len(tags) >= 5 else "needs_work"
        score += 10.0 if has_transcript else 0.0
        breakdown["transcript"] = bool(has_transcript)
        score += 10.0 if has_thumbnail else 0.0
        breakdown["thumbnail"] = bool(has_thumbnail)
        overall = round(min(100.0, score), 1)
        return {"score": overall, "rating": "excellent" if overall >= 80 else "good" if overall >= 60 else "poor", "breakdown": breakdown}

    def keyword_suggestions(self, *, seed: str) -> dict:
        """Expand a seed into YouTube-style keyword suggestions."""
        variations = [
            seed,
            f"como {seed}",
            f"melhor {seed}",
            f"{seed} tutorial",
            f"{seed} para iniciantes",
            f"{seed} 2026",
        ]
        return {"seed": seed, "suggestions": variations, "count": len(variations)}

    def stats(self) -> dict[str, int]:
        return {"criteria": 5}


_SEO: YoutubeSeo | None = None


def get_youtube_seo() -> YoutubeSeo:
    """Get the module-level singleton YouTube SEO helper."""
    global _SEO
    if _SEO is None:
        _SEO = YoutubeSeo()
    return _SEO
