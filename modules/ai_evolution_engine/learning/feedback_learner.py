"""Feedback learner: applies user feedback to recommendation weights."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FeedbackRecord:
    """Accepted/rejected feedback for a recommendation kind."""

    kind: str
    accepted_count: int = 0
    rejected_count: int = 0

    @property
    def acceptance_ratio(self) -> float:
        total = self.accepted_count + self.rejected_count
        if total == 0:
            return 0.0
        return self.accepted_count / total

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "acceptance_ratio": self.acceptance_ratio,
        }


class FeedbackLearner:
    """Tracks acceptance per kind; engine can damp disliked kinds."""

    def __init__(self, max_kinds: int = 200) -> None:
        self._records: dict[str, FeedbackRecord] = {}
        self._max = max_kinds

    def apply(self, kind: str, accepted: bool) -> None:
        record = self._records.setdefault(kind, FeedbackRecord(kind=kind))
        if accepted:
            record.accepted_count += 1
        else:
            record.rejected_count += 1

    def dampen_factor(self, kind: str) -> float:
        """1.0 = no damping; approaches 0.5 as rejections dominate."""
        record = self._records.get(kind)
        if record is None or record.accepted_count >= record.rejected_count:
            return 1.0
        return max(0.5, 1.0 - record.rejected_count * 0.05)

    def all(self) -> list[FeedbackRecord]:
        return list(self._records.values())
