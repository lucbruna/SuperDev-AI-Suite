"""Streaming Analytics — live session performance metrics (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class StreamingAnalytics:
    """Aggregate live stream metrics and derive insights."""

    def __init__(self) -> None:
        self._sessions: list[dict] = []

    def ingest(self, *, session: dict) -> dict:
        self._sessions.append(dict(session))
        return {"ingested": 1, "total": len(self._sessions)}

    def summary(self) -> dict:
        keys = ["peak_viewers", "avg_viewers", "watch_minutes", "new_followers", "chat_messages"]
        totals: dict[str, float] = {k: 0.0 for k in keys}
        for session in self._sessions:
            for key in keys:
                totals[key] += session.get(key, 0) or 0
        totals["avg_peak_viewers"] = (
            round(totals["peak_viewers"] / len(self._sessions), 1) if self._sessions else 0.0
        )
        return totals

    def best_session(self) -> dict | None:
        """Return the session with the highest peak viewers."""
        if not self._sessions:
            return None
        return max(self._sessions, key=lambda s: s.get("peak_viewers", 0) or 0)

    def stats(self) -> dict[str, int]:
        return {"sessions": len(self._sessions)}


_ANALYTICS: StreamingAnalytics | None = None


def get_streaming_analytics() -> StreamingAnalytics:
    """Get the module-level singleton streaming analytics."""
    global _ANALYTICS
    if _ANALYTICS is None:
        _ANALYTICS = StreamingAnalytics()
    return _ANALYTICS
