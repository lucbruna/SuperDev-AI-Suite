"""Unit tests: analytics and recommendation packages."""
from __future__ import annotations

from modules.ai_evolution_engine.analytics.analytics_engine import AnalyticsEngine
from modules.ai_evolution_engine.config.constants import REC_PERFORMANCE
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)
from modules.ai_evolution_engine.recommendation.recommendation_engine import (
    RecommendationEngine,
)
from modules.ai_evolution_engine.tests.helpers import make_context


def test_analytics_compute_deterministic_slices():
    ctx = make_context(
        dependency_count=12,
        duplicate_dependencies=3,
    )
    analytics = AnalyticsEngine()
    slices = analytics.compute(ctx)

    by_name = {s.name: s for s in slices}
    assert by_name["dependency_count"].value == 12.0
    assert by_name["duplicate_dependencies"].value == 3.0
    assert by_name["cycles"].value == 0.0


def test_analytics_slices_returns_last_compute():
    ctx = make_context()
    analytics = AnalyticsEngine()
    analytics.compute(ctx)
    assert len(analytics.slices()) > 0


def test_recommendation_priority_weighted():
    rec = Recommendation(
        kind="architecture",
        title="t",
        impact_score=1.0,
        effort_score=1.0,
        risk_score=1.0,
    )
    assert rec.priority(0.5, 0.2, 0.3) == 0.0
    high = Recommendation(kind="architecture", title="h", impact_score=1.0)
    low = Recommendation(kind="architecture", title="l", impact_score=0.1)
    assert high.priority() > low.priority()


def test_recommendation_engine_filters_and_sorts():
    def generator(ctx):
        return [
            Recommendation(kind=REC_PERFORMANCE, title="low", impact_score=0.2),
            Recommendation(kind="unknown_kind", title="filtered", impact_score=1.0),
            Recommendation(kind=REC_PERFORMANCE, title="high", impact_score=0.9),
        ]

    engine = RecommendationEngine(generators=[generator])
    result = engine.generate(make_context())

    titles = [r.title for r in result]
    assert titles == ["high", "low"]


def test_recommendation_to_dict_roundtrip():
    rec = Recommendation(kind="architecture", title="t", evidence=["e1"])
    payload = rec.to_dict()
    assert payload["kind"] == "architecture"
    assert payload["evidence"] == ["e1"]
    assert "priority" in payload
