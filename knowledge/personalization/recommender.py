from __future__ import annotations

import logging
from typing import Any

from .profiler import UserProfiler


class Recommender:
    """Recommends content based on user interests and topic overlap."""

    def __init__(self, profiler: UserProfiler | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.personalization.recommender")
        self.profiler = profiler or UserProfiler()

    def recommend(self, user_id: str, candidates: list[dict[str, Any]], top_k: int = 3) -> list[dict[str, Any]]:
        interests = dict(self.profiler.interests(user_id))
        if not interests:
            return candidates[:top_k]
        scored = []
        for candidate in candidates:
            topics = candidate.get("topics") or []
            score = sum(interests.get(topic, 0.0) for topic in topics)
            scored.append((score, candidate))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [candidate for _score, candidate in scored[:top_k]]
