from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class FeedbackManager:
    def __init__(self) -> None:
        self._feedback_store: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("FeedbackManager initialized")

    async def stop(self) -> None:
        self._feedback_store.clear()
        self._initialized = False
        logger.info("FeedbackManager stopped")

    async def register_feedback(self, feedback_data: dict[str, Any]) -> str:
        feedback_id = str(uuid.uuid4())
        entry = {
            "id": feedback_id,
            "data": feedback_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analyzed": False,
            "sentiment": feedback_data.get("sentiment", "neutral"),
            "source": feedback_data.get("source", "unknown"),
            "rating": feedback_data.get("rating"),
        }
        self._feedback_store[feedback_id] = entry
        logger.debug("Registered feedback %s", feedback_id)
        return feedback_id

    async def collect_feedback(self, source: str, raw_data: Any) -> dict[str, Any]:
        feedback_id = str(uuid.uuid4())
        rating = None
        sentiment = "neutral"

        if isinstance(raw_data, dict):
            rating = raw_data.get("rating")
            sentiment = raw_data.get("sentiment", "neutral")
        elif isinstance(raw_data, (int, float)):
            rating = raw_data
            sentiment = "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral"

        entry = {
            "id": feedback_id,
            "source": source,
            "raw_data": raw_data,
            "rating": rating,
            "sentiment": sentiment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analyzed": False,
        }
        self._feedback_store[feedback_id] = entry
        return entry

    async def analyze_feedback(self, feedback_id: str) -> dict[str, Any]:
        entry = self._feedback_store.get(feedback_id)
        if not entry:
            return {"error": "feedback_not_found"}

        rating = entry.get("rating")
        sentiment = entry.get("sentiment", "neutral")

        analysis = {
            "id": feedback_id,
            "sentiment": sentiment,
            "is_positive": sentiment == "positive",
            "is_negative": sentiment == "negative",
            "requires_action": sentiment == "negative" or (rating is not None and rating < 3),
            "rating_category": "high" if rating and rating >= 4 else "medium" if rating and rating >= 3 else "low" if rating else "unrated",
        }

        entry["analyzed"] = True
        entry["analysis"] = analysis
        return analysis

    async def get_feedback_summary(self) -> dict[str, Any]:
        if not self._feedback_store:
            return {"total_feedback": 0, "summary": "no_feedback"}

        sentiments = defaultdict(int)
        ratings = []
        sources = defaultdict(int)

        for entry in self._feedback_store.values():
            sentiments[entry.get("sentiment", "neutral")] += 1
            sources[entry.get("source", "unknown")] += 1
            if entry.get("rating") is not None:
                ratings.append(entry["rating"])

        avg_rating = sum(ratings) / len(ratings) if ratings else None

        return {
            "total_feedback": len(self._feedback_store),
            "sentiment_breakdown": dict(sentiments),
            "source_breakdown": dict(sources),
            "average_rating": avg_rating,
            "analyzed_count": sum(1 for e in self._feedback_store.values() if e.get("analyzed")),
        }

    async def close_feedback_loop(self, feedback_id: str, resolution: dict[str, Any]) -> dict[str, Any]:
        entry = self._feedback_store.get(feedback_id)
        if not entry:
            return {"error": "feedback_not_found"}

        entry["resolved"] = True
        entry["resolution"] = resolution
        entry["resolved_at"] = datetime.now(timezone.utc).isoformat()

        return {
            "id": feedback_id,
            "status": "closed",
            "resolution": resolution,
        }

    def get_feedback(self, feedback_id: str) -> Optional[dict[str, Any]]:
        return self._feedback_store.get(feedback_id)
