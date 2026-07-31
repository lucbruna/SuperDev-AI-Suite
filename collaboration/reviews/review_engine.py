"""Review engine: código e segurança.

Fluxo: Coder implementa -> Human Developer revisa -> Security revisa
(se security) -> Testing valida.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import (ReviewKind, ReviewRecord,
                                                ReviewStatus)
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.reviews.review_criteria import ReviewCriteria
from collaboration.reviews.review_findings import (make_finding,
                                                   sort_findings)
from collaboration.reviews.review_manager import ReviewManager
from collaboration.reviews.review_metrics import ReviewMetrics


class ReviewEngine:
    """Orquestrador de reviews (Fase 6 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 manager: ReviewManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.security = security or CollaborationSecurity()
        self.manager = manager or ReviewManager(registry=registry)
        self.criteria = ReviewCriteria()

    def create(self, target_kind: ReviewKind, target_id: str,
               author_id: str) -> ReviewRecord:
        review = self.manager.create(target_kind, target_id, author_id)
        self.metrics.increment("collab.reviews")
        self.events.publish(CollaborationEventType.REVIEW_CREATED,
                            {"review_id": review.review_id,
                             "target_kind": target_kind.value,
                             "target_id": target_id})
        return review

    def get(self, review_id: str) -> ReviewRecord | None:
        return self.manager.get(review_id)

    def list(self) -> list[str]:
        return self.manager.list()

    def remove(self, review_id: str) -> bool:
        return self.manager.remove(review_id)

    def decide(self, review_id: str, status: ReviewStatus, score: float,
               findings: list[dict[str, Any]]) -> ReviewRecord | None:
        review = self.manager.decide(review_id, status, score, findings)
        if review is not None:
            self.events.publish(CollaborationEventType.REVIEW_DECIDED,
                                {"review_id": review_id,
                                 "status": status.value,
                                 "score": review.score})
        return review

    def decide_auto(self, review_id: str,
                    findings: list[dict[str, Any]]) -> ReviewRecord | None:
        """Decides a review from findings using the metrics heuristics."""
        review = self.get(review_id)
        if review is None:
            return None
        checklist = self.criteria.checklist(review.target_kind)
        # Automatic decision: criteria not flagged by findings pass.
        for item in checklist:
            if item.get("passed") is None:
                item["passed"] = True
        base = self.manager.metrics.score_from_criteria(checklist)
        score = self.manager.metrics.adjusted_score(base, findings)
        verdict = self.manager.metrics.verdict(score, findings)
        status = ReviewStatus(verdict)
        return self.decide(review_id, status, score, sort_findings(findings))

    def checklist(self, kind: ReviewKind) -> list[dict[str, Any]]:
        return self.criteria.checklist(kind)

    def finding(self, severity: str, message: str,
                location: str = "") -> dict[str, Any]:
        return make_finding(severity, message, location)

    def by_target(self, target_id: str) -> list[ReviewRecord]:
        return self.manager.by_target(target_id)

    def stats(self) -> dict[str, Any]:
        return {"reviews": self.manager.count()}
