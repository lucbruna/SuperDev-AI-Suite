"""LinkedIn Analytics — aggregates LinkedIn performance metrics (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class LinkedInAnalytics:
    """Aggregate LinkedIn metrics and derive engagement insights."""

    def __init__(self) -> None:
        self._posts: list[dict] = []

    def ingest(self, *, post: dict) -> dict:
        self._posts.append(dict(post))
        return {"ingested": 1, "total": len(self._posts)}

    def summary(self) -> dict:
        keys = ["impressions", "clicks", "likes", "comments", "shares", "followers_gained"]
        totals: dict[str, float] = {k: 0.0 for k in keys}
        for post in self._posts:
            for key in keys:
                totals[key] += post.get(key, 0) or 0
        totals["ctr"] = (
            round(totals["clicks"] / totals["impressions"] * 100.0, 2) if totals["impressions"] else 0.0
        )
        totals["engagement_rate"] = (
            round(
                (totals["likes"] + totals["comments"] + totals["shares"]) / totals["impressions"] * 100.0, 2
            )
            if totals["impressions"]
            else 0.0
        )
        return totals

    def top_post(self) -> dict | None:
        """Return the post with the highest engagement."""
        if not self._posts:
            return None
        return max(
            self._posts,
            key=lambda p: (p.get("likes", 0) or 0) + (p.get("comments", 0) or 0) + (p.get("shares", 0) or 0),
        )

    def stats(self) -> dict[str, int]:
        return {"posts": len(self._posts)}


_ANALYTICS: LinkedInAnalytics | None = None


def get_linkedin_analytics() -> LinkedInAnalytics:
    """Get the module-level singleton LinkedIn analytics."""
    global _ANALYTICS
    if _ANALYTICS is None:
        _ANALYTICS = LinkedInAnalytics()
    return _ANALYTICS
