"""Social Analytics — aggregates engagement metrics across platforms (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class SocialAnalytics:
    """Aggregate and compare social engagement metrics."""

    def __init__(self) -> None:
        self._data: dict[str, list[dict]] = {}

    def ingest(self, *, platform: str, posts: list[dict]) -> dict:
        """Store per-post metrics for a platform."""
        self._data.setdefault(platform.lower(), []).extend(posts)
        return {"ingested": len(posts), "platform": platform.lower()}

    def summary(self, *, platform: str | None = None) -> dict:
        """Summarize engagement per platform (or all platforms)."""
        platforms = [platform.lower()] if platform else list(self._data)
        out: dict[str, dict[str, float]] = {}
        for name in platforms:
            posts = self._data.get(name, [])
            totals: dict[str, float] = {"posts": float(len(posts)), "likes": 0.0, "comments": 0.0, "shares": 0.0, "views": 0.0}
            for post in posts:
                for key in ("likes", "comments", "shares", "views"):
                    totals[key] += post.get(key, 0) or 0
            totals["engagement_rate"] = (
                round(
                    (totals["likes"] + totals["comments"] + totals["shares"])
                    / totals["views"] * 100.0, 2
                )
                if totals["views"]
                else 0.0
            )
            out[name] = totals
        return out

    def stats(self) -> dict[str, int]:
        return {"platforms": len(self._data)}


_ANALYTICS: SocialAnalytics | None = None


def get_social_analytics() -> SocialAnalytics:
    """Get the module-level singleton social analytics."""
    global _ANALYTICS
    if _ANALYTICS is None:
        _ANALYTICS = SocialAnalytics()
    return _ANALYTICS
