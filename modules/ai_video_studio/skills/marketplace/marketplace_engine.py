"""Marketplace engine — facade over publish → review → rate → install flow."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.marketplace.dependency_checker import (
    DependencyChecker,
)
from modules.ai_video_studio.skills.marketplace.publisher import MarketPublisher
from modules.ai_video_studio.skills.marketplace.rating import MarketRating
from modules.ai_video_studio.skills.marketplace.reviewer import MarketReviewer
from modules.ai_video_studio.skills.skill_marketplace import get_skill_marketplace


class MarketplaceEngine:
    """Coordinates submission, review, rating and dependency validation."""

    def __init__(self) -> None:
        self.publisher = MarketPublisher()
        self.reviewer = MarketReviewer(self.publisher)
        self.rating = MarketRating()
        self.dependencies = DependencyChecker()

    def snapshot(self) -> dict[str, Any]:
        catalog = get_skill_marketplace()
        return {
            "catalog_count": len(catalog.list()),
            "submissions": self.publisher.list(),
            "pending_review": self.reviewer.pending(),
            "top_rated": self.rating.top(),
        }


_engine: MarketplaceEngine | None = None


def get_marketplace_engine() -> MarketplaceEngine:
    global _engine
    if _engine is None:
        _engine = MarketplaceEngine()
    return _engine
