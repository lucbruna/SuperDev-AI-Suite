"""Tests for the knowledge personalization subsystem."""

from __future__ import annotations

import pytest

from knowledge.personalization import (
    PersonalizationEngine,
    Preferences,
    Recommender,
    UserProfiler,
)


class TestPreferences:
    def test_set_get_update(self) -> None:
        preferences = Preferences("user-1")
        assert preferences.user_id == "user-1"
        preferences.set("lang", "pt")
        assert preferences.get("lang") == "pt"
        assert preferences.get("missing", "default") == "default"
        preferences.update({"theme": "dark"})
        assert preferences.all() == {"lang": "pt", "theme": "dark"}
        assert preferences.to_dict()["user_id"] == "user-1"


class TestUserProfiler:
    def test_record_interaction_and_interests(self) -> None:
        profiler = UserProfiler()
        profiler.record_interaction("user-1", "python", weight=2.0)
        profiler.record_interaction("user-1", "api", weight=1.0)
        interests = profiler.interests("user-1")
        assert interests[0] == ("python", 2.0)
        assert profiler.interests("unknown") == []

    def test_profile(self) -> None:
        profiler = UserProfiler()
        assert profiler.profile("unknown")["count"] == 0
        profiler.record_interaction("user-1", "rag")
        profile = profiler.profile("user-1")
        assert profile["count"] == 1
        assert profile["interests"] == [("rag", 1.0)]

    def test_apply_preferences(self) -> None:
        profiler = UserProfiler()
        profiler.record_interaction("user-1", "search")
        preferences = Preferences("user-1")
        result = profiler.apply_preferences("user-1", preferences)
        assert result.get("topics") == ["search"]

    def test_clear(self) -> None:
        profiler = UserProfiler()
        profiler.record_interaction("user-1", "x")
        profiler.clear("user-1")
        assert profiler.interests("user-1") == []
        profiler.record_interaction("user-1", "x")
        profiler.record_interaction("user-2", "y")
        profiler.clear()
        assert profiler.interests("user-1") == []
        assert profiler.interests("user-2") == []


class TestRecommender:
    def test_recommend_scores_by_interest(self) -> None:
        profiler = UserProfiler()
        profiler.record_interaction("user-1", "python", weight=3.0)
        recommender = Recommender(profiler)
        candidates = [
            {"id": "c1", "topics": ["python", "api"]},
            {"id": "c2", "topics": ["marketing"]},
        ]
        recommended = recommender.recommend("user-1", candidates, top_k=2)
        assert recommended[0]["id"] == "c1"

    def test_recommend_without_interests(self) -> None:
        recommender = Recommender()
        candidates = [{"id": "c1"}, {"id": "c2"}]
        assert recommender.recommend("new-user", candidates, top_k=1) == [{"id": "c1"}]


class TestPersonalizationEngine:
    def test_observe_and_interests(self) -> None:
        engine = PersonalizationEngine()
        engine.observe("user-1", "python", weight=2.0)
        engine.observe("user-1", "python", weight=1.0)
        interests = engine.interests("user-1")
        assert interests[0] == ("python", 3.0)

    def test_preferences_and_recommend(self) -> None:
        engine = PersonalizationEngine()
        preferences = engine.preferences("user-1")
        preferences.set("lang", "pt")
        assert engine.preferences("user-1").get("lang") == "pt"
        engine.observe("user-1", "rag")
        recommended = engine.recommend("user-1", [{"id": "a", "topics": ["rag"]}])
        assert recommended[0]["id"] == "a"

    def test_stats(self) -> None:
        engine = PersonalizationEngine()
        engine.observe("user-1", "topic")
        assert engine.stats()["users"] == 1
