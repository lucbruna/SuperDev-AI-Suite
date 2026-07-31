"""Learning subsystem engine — Continuous learning from experiences."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ExperienceType(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"


class ImprovementType(Enum):
    CODE = "code"
    PROCESS = "process"
    ARCHITECTURE = "architecture"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class Experience:
    experience_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    experience_type: ExperienceType = ExperienceType.NEUTRAL
    context: dict[str, Any] = field(default_factory=dict)
    outcome: str = ""
    lessons: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Improvement:
    improvement_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    improvement_type: ImprovementType = ImprovementType.CODE
    priority: int = 5
    estimated_impact: float = 0.5
    experience_ids: list[str] = field(default_factory=list)
    implemented: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FeedbackEntry:
    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source: str = ""
    rating: float = 0.5
    comment: str = ""
    category: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class LearningSubEngine:
    def __init__(self):
        self._experiences: dict[str, Experience] = {}
        self._improvements: dict[str, Improvement] = {}
        self._feedback: list[FeedbackEntry] = []
        self._patterns: list[dict[str, Any]] = []

    def record_experience(
        self,
        title: str,
        description: str,
        experience_type: str = "neutral",
        outcome: str = "",
        lessons: list[str] | None = None,
    ) -> Experience:
        et = (
            ExperienceType(experience_type)
            if experience_type in [e.value for e in ExperienceType]
            else ExperienceType.NEUTRAL
        )
        exp = Experience(
            title=title, description=description, experience_type=et, outcome=outcome, lessons=lessons or []
        )
        self._experiences[exp.experience_id] = exp
        return exp

    def get_experience(self, experience_id: str) -> Experience | None:
        return self._experiences.get(experience_id)

    def add_feedback(self, source: str, rating: float, comment: str = "", category: str = "") -> FeedbackEntry:
        fb = FeedbackEntry(source=source, rating=rating, comment=comment, category=category)
        self._feedback.append(fb)
        return fb

    def get_feedback(self, category: str | None = None) -> list[FeedbackEntry]:
        fb = list(self._feedback)
        if category:
            fb = [f for f in fb if f.category == category]
        return fb

    def suggest_improvement(
        self, title: str, description: str, improvement_type: str = "code", priority: int = 5
    ) -> Improvement:
        it = (
            ImprovementType(improvement_type)
            if improvement_type in [e.value for e in ImprovementType]
            else ImprovementType.CODE
        )
        imp = Improvement(title=title, description=description, improvement_type=it, priority=priority)
        self._improvements[imp.improvement_id] = imp
        return imp

    def get_improvement(self, improvement_id: str) -> Improvement | None:
        return self._improvements.get(improvement_id)

    def implement_improvement(self, improvement_id: str) -> bool:
        imp = self._improvements.get(improvement_id)
        if not imp:
            return False
        imp.implemented = True
        return True

    def analyze_patterns(self) -> list[dict[str, Any]]:
        patterns = []
        type_counts = {}
        for exp in self._experiences.values():
            t = exp.experience_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
        for t, count in type_counts.items():
            if count > 1:
                patterns.append({"pattern": f"frequent_{t}", "count": count, "type": t})
        self._patterns = patterns
        return patterns

    def get_lessons_learned(self) -> list[str]:
        lessons = []
        for exp in self._experiences.values():
            lessons.extend(exp.lessons)
        return list(set(lessons))

    def get_top_improvements(self, limit: int = 5) -> list[Improvement]:
        imps = [i for i in self._improvements.values() if not i.implemented]
        return sorted(imps, key=lambda i: i.priority, reverse=True)[:limit]

    def get_stats(self) -> dict:
        experiences = list(self._experiences.values())
        return {
            "total_experiences": len(experiences),
            "successes": len([e for e in experiences if e.experience_type == ExperienceType.SUCCESS]),
            "failures": len([e for e in experiences if e.experience_type == ExperienceType.FAILURE]),
            "total_improvements": len(self._improvements),
            "implemented": len([i for i in self._improvements.values() if i.implemented]),
            "total_feedback": len(self._feedback),
            "patterns_found": len(self._patterns),
        }
