from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_metrics import KnowledgeMetrics
from .preferences import Preferences
from .profiler import UserProfiler
from .recommender import Recommender


class PersonalizationEngine:
    """Composes profiling, preferences, and recommendations per user."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.personalization.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.profiler = UserProfiler()
        self.recommender = Recommender(self.profiler)
        self._preferences: dict[str, Preferences] = {}

    def observe(self, user_id: str, topic: str, weight: float = 1.0) -> None:
        self.profiler.record_interaction(user_id, topic, weight)
        self.metrics.increment("personalization.interactions")

    def preferences(self, user_id: str) -> Preferences:
        prefs = self._preferences.get(user_id)
        if prefs is None:
            prefs = Preferences(user_id)
            self._preferences[user_id] = prefs
        return prefs

    def interests(self, user_id: str, top_k: int = 5) -> list[tuple[str, float]]:
        return self.profiler.interests(user_id, top_k)

    def recommend(self, user_id: str, candidates: list[dict[str, Any]], top_k: int = 3) -> list[dict[str, Any]]:
        return self.recommender.recommend(user_id, candidates, top_k)

    def stats(self) -> dict[str, Any]:
        return {"users": len(self._profiles())}

    def _profiles(self) -> dict[str, Any]:
        return getattr(self.profiler, "_profiles", {})
