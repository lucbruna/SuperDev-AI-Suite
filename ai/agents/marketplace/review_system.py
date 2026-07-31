"""Review system for marketplace agents."""
from __future__ import annotations

import time
from typing import Any


class ReviewSystem:
    """Manages user reviews and ratings for marketplace agents."""

    def __init__(self) -> None:
        self._reviews: dict[str, list[dict[str, Any]]] = {}

    def add_review(self, agent_id: str, rating: float, text: str) -> dict[str, Any]:
        if agent_id not in self._reviews:
            self._reviews[agent_id] = []
        review = {
            "rating": min(max(rating, 0.0), 5.0),
            "text": text,
            "timestamp": time.time(),
        }
        self._reviews[agent_id].append(review)
        avg = sum(r["rating"] for r in self._reviews[agent_id]) / len(self._reviews[agent_id])
        return {
            "status": "review_added",
            "agent_id": agent_id,
            "average_rating": round(avg, 2),
            "total_reviews": len(self._reviews[agent_id]),
        }

    def get_reviews(self, agent_id: str) -> list[dict[str, Any]]:
        return list(self._reviews.get(agent_id, []))

    def get_average(self, agent_id: str) -> float:
        reviews = self._reviews.get(agent_id, [])
        if not reviews:
            return 0.0
        return round(sum(r["rating"] for r in reviews) / len(reviews), 2)

    def count(self) -> int:
        return sum(len(r) for r in self._reviews.values())
