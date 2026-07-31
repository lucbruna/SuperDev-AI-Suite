"""
Post-Incident Review and Lessons Learned
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RootCauseCategory(Enum):
    HUMAN_ERROR = "human_error"
    PROCESS_FAILURE = "process_failure"
    TECHNICAL_FAILURE = "technical_failure"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


@dataclass
class RootCause:
    cause_id: str
    category: RootCauseCategory
    description: str = ""
    impact: str = ""


@dataclass
class Improvement:
    improvement_id: str
    title: str
    description: str = ""
    owner: str = ""
    status: str = "open"
    priority: str = "medium"
    due_date: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class LessonsLearned:
    review_id: str
    incident_id: str
    root_causes: list[RootCause] = field(default_factory=list)
    improvements: list[Improvement] = field(default_factory=list)
    what_went_well: list[str] = field(default_factory=list)
    what_went_wrong: list[str] = field(default_factory=list)
    review_date: datetime = field(default_factory=datetime.now)
    participants: list[str] = field(default_factory=list)


class LessonsLearnedManager:
    def __init__(self):
        self.reviews: dict[str, LessonsLearned] = {}
        self.improvements: dict[str, Improvement] = {}
        self.knowledge_base: list[dict[str, Any]] = []

    def create_review(self, incident_id: str, participants: list[str] = None) -> LessonsLearned:
        review_id = hashlib.sha256(f"{incident_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        review = LessonsLearned(review_id=review_id, incident_id=incident_id, participants=participants or [])
        self.reviews[review_id] = review
        return review

    def add_root_cause(self, review_id: str, category: RootCauseCategory, description: str = "") -> RootCause | None:
        review = self.reviews.get(review_id)
        if review:
            cause = RootCause(cause_id=f"rc_{len(review.root_causes)}", category=category, description=description)
            review.root_causes.append(cause)
            return cause
        return None

    def add_improvement(self, review_id: str, title: str, description: str = "", owner: str = "") -> Improvement | None:
        review = self.reviews.get(review_id)
        if review:
            improvement = Improvement(
                improvement_id=f"imp_{len(self.improvements)}", title=title, description=description, owner=owner
            )
            review.improvements.append(improvement)
            self.improvements[improvement.improvement_id] = improvement
            return improvement
        return None

    def add_what_went_well(self, review_id: str, item: str) -> bool:
        review = self.reviews.get(review_id)
        if review:
            review.what_went_well.append(item)
            return True
        return False

    def add_what_went_wrong(self, review_id: str, item: str) -> bool:
        review = self.reviews.get(review_id)
        if review:
            review.what_went_wrong.append(item)
            return True
        return False

    def update_improvement_status(self, improvement_id: str, status: str) -> bool:
        if improvement_id in self.improvements:
            self.improvements[improvement_id].status = status
            if status == "completed":
                self.improvements[improvement_id].completed_at = datetime.now()
            return True
        return False

    def get_review(self, review_id: str) -> LessonsLearned | None:
        return self.reviews.get(review_id)

    def get_open_improvements(self) -> list[Improvement]:
        return [i for i in self.improvements.values() if i.status == "open"]

    def count(self) -> int:
        return len(self.reviews)
