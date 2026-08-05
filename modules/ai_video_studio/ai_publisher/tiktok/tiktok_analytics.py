"""TikTok Analytics — aggregates TikTok performance metrics (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class TikTokAnalytics:
    """Aggregate TikTok metrics and derive engagement insights."""

    def __init__(self) -> None:
        self._posts: list[dict] = []

    def ingest(self, *, post: dict) -> dict:
        self._posts.append(dict(post))
        return {"ingested": 1, "total": len(self._posts)}

    def summary(self) -> dict:
        keys = ["views", "likes", "comments", "shares", "saves", "watch_time_seconds"]
        totals: dict[str, float] = {k: 0.0 for k in keys}
        for post in self._posts:
            for key in keys:
                totals[key] += post.get(key, 0) or 0
        totals["engagement_rate"] = (
            round(
                (totals["likes"] + totals["comments"] + totals["shares"] + totals["saves"])
                / totals["views"] * 100.0, 2
            )
            if totals["views"]
            else 0.0
        )
        return totals

    def completion_rate(self) -> float:
        """Average video completion rate across posts."""
        rates = [p.get("completion_rate", 0) for p in self._posts if p.get("completion_rate") is not None]
        if not rates:
            return 0.0
        return round(sum(rates) / len(rates), 2)

    def stats(self) -> dict[str, int]:
        return {"posts": len(self._posts)}


_ANALYTICS: TikTokAnalytics | None = None


def get_tiktok_analytics() -> TikTokAnalytics:
    """Get the module-level singleton TikTok analytics."""
    global _ANALYTICS
    if _ANALYTICS is None:
        _ANALYTICS = TikTokAnalytics()
    return _ANALYTICS
