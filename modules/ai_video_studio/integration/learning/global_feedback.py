"""Global Feedback — aggregates studio-wide user feedback events."""
from __future__ import annotations

from typing import Any


class GlobalFeedback:
    """Counts feedback by sentiment."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def submit(self, user_id: str, sentiment: str, message: str = "") -> dict[str, Any]:
        sentiment = sentiment if sentiment in ("positive", "negative", "neutral") else "neutral"
        event = {"user": user_id, "sentiment": sentiment, "message": message}
        self._events.append(event)
        return {"recorded": len(self._events)}

    def summary(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for e in self._events:
            counts[e["sentiment"]] = counts.get(e["sentiment"], 0) + 1
        return {"events": len(self._events), "by_sentiment": counts}


_global_feedback: GlobalFeedback | None = None


def get_global_feedback() -> GlobalFeedback:
    global _global_feedback
    if _global_feedback is None:
        _global_feedback = GlobalFeedback()
    return _global_feedback
