"""YouTube Analytics — aggregates channel and video performance metrics (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class YoutubeAnalytics:
    """Aggregate YouTube performance metrics and derive insights."""

    def __init__(self) -> None:
        self._videos: list[dict] = []

    def ingest(self, *, video: dict) -> dict:
        """Store per-video performance stats."""
        self._videos.append(dict(video))
        return {"ingested": 1, "total": len(self._videos)}

    def totals(self) -> dict:
        """Sum performance metrics across ingested videos."""
        keys = ["views", "likes", "comments", "shares", "watch_time_hours", "subscribers_gained"]
        totals: dict[str, float] = {k: 0.0 for k in keys}
        for video in self._videos:
            for key in keys:
                totals[key] += video.get(key, 0) or 0
        return totals

    def average_ctr(self) -> float:
        """Average click-through rate across videos."""
        ctrs = [v.get("ctr", 0) for v in self._videos if v.get("ctr") is not None]
        if not ctrs:
            return 0.0
        return round(sum(ctrs) / len(ctrs), 2)

    def average_view_duration_seconds(self) -> float:
        """Average view duration across videos."""
        durations = [v.get("avg_view_duration", 0) for v in self._videos if v.get("avg_view_duration")]
        if not durations:
            return 0.0
        return round(sum(durations) / len(durations), 1)

    def top_videos(self, *, metric: str = "views", limit: int = 5) -> list[dict]:
        """Return the top videos by a metric."""
        ranked = sorted(self._videos, key=lambda v: v.get(metric, 0) or 0, reverse=True)
        return ranked[:limit]

    def stats(self) -> dict[str, int]:
        return {"videos": len(self._videos)}


_ANALYTICS: YoutubeAnalytics | None = None


def get_youtube_analytics() -> YoutubeAnalytics:
    """Get the module-level singleton YouTube analytics."""
    global _ANALYTICS
    if _ANALYTICS is None:
        _ANALYTICS = YoutubeAnalytics()
    return _ANALYTICS
