"""Review lifecycle management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import (ReviewKind, ReviewRecord,
                                                ReviewStatus)
from collaboration.collaboration_protocols import new_id
from collaboration.reviews.review_metrics import ReviewMetrics


class ReviewManager:
    """CRUD for reviews plus scoring helpers."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry
        self.metrics = ReviewMetrics()

    def create(self, target_kind: ReviewKind, target_id: str,
               author_id: str) -> ReviewRecord:
        review = ReviewRecord(review_id=new_id("rev"),
                              target_kind=target_kind, target_id=target_id,
                              author_id=author_id)
        if self.registry is not None:
            self.registry.register_review(review.review_id, review)
        return review

    def get(self, review_id: str) -> ReviewRecord | None:
        if self.registry is None:
            return None
        return self.registry.get_review(review_id)

    def list(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_reviews()

    def remove(self, review_id: str) -> bool:
        if self.registry is not None:
            return self.registry.remove_review(review_id)
        return False

    def decide(self, review_id: str, status: ReviewStatus, score: float,
               findings: list[dict[str, Any]]) -> ReviewRecord | None:
        review = self.get(review_id)
        if review is None:
            return None
        review.status = status
        review.score = max(0.0, min(100.0, float(score)))
        review.findings = list(findings)
        return review

    def by_target(self, target_id: str) -> list[ReviewRecord]:
        if self.registry is None:
            return []
        reviews = []
        for review_id in self.registry.list_reviews():
            review = self.registry.get_review(review_id)
            if review is not None and review.target_id == target_id:
                reviews.append(review)
        return reviews

    def count(self) -> int:
        if self.registry is None:
            return 0
        return len(self.registry.list_reviews())
