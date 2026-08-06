"""Unit tests: roadmap package."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import (
    ITEM_PLANNED,
    REC_APPROVED,
    REC_DRAFT,
)
from modules.ai_evolution_engine.roadmap.roadmap_engine import (
    RoadmapEngine,
    RoadmapItem,
    RoadmapPlan,
)
from modules.ai_evolution_engine.tests.helpers import make_recommendation


def test_roadmap_engine_plans_only_approved():
    approved = make_recommendation(title="approved item", impact_score=0.9)
    approved.status = REC_APPROVED
    draft = make_recommendation(title="draft item")
    draft.status = REC_DRAFT

    plan = RoadmapEngine().plan([approved, draft])

    assert isinstance(plan, RoadmapPlan)
    assert len(plan.items) == 1
    assert plan.items[0].recommendation_title == "approved item"
    assert plan.items[0].status == ITEM_PLANNED


def test_roadmap_items_sorted_by_priority():
    low = make_recommendation(title="low", impact_score=0.2)
    low.status = REC_APPROVED
    high = make_recommendation(title="high", impact_score=0.9)
    high.status = REC_APPROVED

    plan = RoadmapEngine().plan([low, high])
    assert [i.recommendation_title for i in plan.items] == ["high", "low"]


def test_roadmap_item_to_dict():
    item = RoadmapItem(
        recommendation_title="t", kind="architecture", priority=0.5
    )
    payload = item.to_dict()
    assert payload["recommendation_title"] == "t"
    assert payload["priority"] == 0.5
