"""TikTok Trends — trend detection and scoring (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class TikTokTrends:
    """Detect and rank emerging TikTok trends."""

    def __init__(self) -> None:
        self._signals: list[dict] = []

    def ingest(self, *, keyword: str, mentions: int, velocity: float = 0.0) -> dict:
        """Record a trend signal (mentions + growth velocity)."""
        signal = {"keyword": keyword, "mentions": mentions, "velocity": velocity}
        self._signals.append(signal)
        return signal

    def top(self, *, limit: int = 10) -> list[dict]:
        """Rank signals by a trend score (mentions + velocity)."""
        scored = [
            {**s, "trend_score": round(s["mentions"] * (1.0 + s["velocity"]), 1)}
            for s in self._signals
        ]
        ranked = sorted(scored, key=lambda s: s["trend_score"], reverse=True)
        return ranked[:limit]

    def stats(self) -> dict[str, int]:
        return {"signals": len(self._signals)}


_TRENDS: TikTokTrends | None = None


def get_tiktok_trends() -> TikTokTrends:
    """Get the module-level singleton trend detector."""
    global _TRENDS
    if _TRENDS is None:
        _TRENDS = TikTokTrends()
    return _TRENDS
