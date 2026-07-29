from __future__ import annotations

import logging
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ExperienceAnalyzer:
    def __init__(self) -> None:
        self._experiences: list[dict[str, Any]] = []
        self._lessons: list[dict[str, Any]] = []
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("ExperienceAnalyzer initialized")

    async def stop(self) -> None:
        self._experiences.clear()
        self._lessons.clear()
        self._initialized = False
        logger.info("ExperienceAnalyzer stopped")

    async def analyze_experience(self, data: Any, context: dict[str, Any]) -> dict[str, Any]:
        experience_id = str(uuid.uuid4())

        if isinstance(data, dict):
            outcome = data.get("outcome", "unknown")
            key_metrics = data.get("metrics", {})
        else:
            outcome = str(data)
            key_metrics = {}

        analysis = {
            "id": experience_id,
            "data": data,
            "context": context,
            "outcome": outcome,
            "key_metrics": key_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lessons_extracted": False,
        }

        self._experiences.append(analysis)
        return analysis

    async def extract_lessons(self, experience_id: Optional[str] = None) -> list[dict[str, Any]]:
        targets = self._experiences
        if experience_id:
            targets = [e for e in self._experiences if e["id"] == experience_id]

        extracted = []
        for exp in targets:
            outcome = exp.get("outcome", "unknown")
            lesson = {
                "id": str(uuid.uuid4()),
                "experience_id": exp["id"],
                "lesson": f"learned_from_{outcome}",
                "outcome": outcome,
                "actionable": outcome not in ("unknown", "neutral"),
                "severity": "high" if outcome in ("failure", "error") else "low",
            }
            self._lessons.append(lesson)
            extracted.append(lesson)
            exp["lessons_extracted"] = True

        return extracted

    async def identify_patterns(self, experiences: list[dict[str, Any]]) -> list[dict[str, Any]]:
        outcomes = [e.get("outcome", "unknown") for e in experiences]
        outcome_counts = Counter(outcomes)

        common_word_counts: Counter = Counter()
        for exp in experiences:
            data = exp.get("data", "")
            if isinstance(data, str):
                for word in data.lower().split():
                    if len(word) > 3:
                        common_word_counts[word] += 1

        patterns = []
        for outcome, count in outcome_counts.most_common(5):
            if count >= 2:
                patterns.append({
                    "pattern": f"repeated_outcome: {outcome}",
                    "frequency": count,
                    "outcome": outcome,
                    "confidence": min(count / max(len(experiences), 1) + 0.5, 1.0),
                })

        for word, count in common_word_counts.most_common(3):
            patterns.append({
                "pattern": f"common_term: {word}",
                "frequency": count,
                "confidence": min(count / max(len(experiences), 1) * 2, 1.0),
            })

        return patterns

    async def compare_with_history(self, current: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
        if not history:
            return {"is_novel": True, "similar_count": 0, "deviation": 0.0}

        current_outcome = current.get("outcome", "unknown")
        similar = [e for e in history if e.get("outcome") == current_outcome]

        similarity = len(similar) / max(len(history), 1) if similar else 0.0

        return {
            "is_novel": len(similar) == 0,
            "similar_count": len(similar),
            "total_history": len(history),
            "deviation": 1.0 - similarity,
        }

    async def generate_recommendations(self, experience: dict[str, Any]) -> list[dict[str, Any]]:
        recommendations = []
        outcome = experience.get("outcome", "unknown")

        if outcome in ("failure", "error"):
            recommendations.append({
                "type": "corrective",
                "action": "review_and_remediate",
                "priority": "high",
                "rationale": f"experience_had_{outcome}_outcome",
            })
        elif outcome in ("success", "improvement"):
            recommendations.append({
                "type": "reinforce",
                "action": "document_and_replicate",
                "priority": "medium",
                "rationale": f"experience_had_{outcome}_outcome",
            })
        else:
            recommendations.append({
                "type": "monitor",
                "action": "gather_more_data",
                "priority": "low",
                "rationale": "insufficient_outcome_clarity",
            })

        return recommendations

    def get_experience(self, experience_id: str) -> Optional[dict[str, Any]]:
        for exp in self._experiences:
            if exp["id"] == experience_id:
                return exp
        return None
