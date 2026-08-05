"""Publisher Optimizer — scores content and suggests publishing optimizations (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_POWER_WORDS = [
    "incrível", "surpreendente", "secreto", "definitivo", "rápido", "fácil",
    "novo", "grátis", "prova", "como", "por que", "melhor", "top", "ultimate",
]


class PublisherOptimizer:
    """Score content packages and produce optimization suggestions."""

    def _title_score(self, title: str) -> float:
        if not title:
            return 0.0
        length = len(title)
        score = 0.0
        if 30 <= length <= 65:
            score += 40.0
        elif 20 <= length < 30 or 65 < length <= 90:
            score += 25.0
        lowered = title.lower()
        power_hits = sum(1 for w in _POWER_WORDS if w in lowered)
        score += min(30.0, power_hits * 10.0)
        if any(c.isdigit() for c in title):
            score += 10.0
        if title.strip().endswith(("?", "!", "…")):
            score += 10.0
        return round(min(100.0, score), 1)

    def _description_score(self, description: str) -> float:
        if not description:
            return 0.0
        words = description.split()
        score = 0.0
        if len(words) >= 50:
            score += 30.0
        elif len(words) >= 20:
            score += 20.0
        lines = description.count("\n") + 1
        score += min(20.0, lines * 4.0)
        score += 20.0 if any(k in description.lower() for k in ["como", "passo", "tutorial", "guia", "lista"]) else 0.0
        return round(min(100.0, score), 1)

    def _tags_score(self, tags: list[str]) -> float:
        if not tags:
            return 0.0
        score = 0.0
        if len(tags) >= 5:
            score += 40.0
        elif len(tags) >= 3:
            score += 25.0
        score += min(30.0, len(tags) * 5.0)
        if len(set(t.lower() for t in tags)) == len(tags):
            score += 30.0
        return round(min(100.0, score), 1)

    def score(self, *, title: str, description: str = "", tags: list[str] | None = None) -> dict:
        """Score a content package and return a breakdown."""
        tags = tags or []
        scores = {
            "title": self._title_score(title),
            "description": self._description_score(description),
            "tags": self._tags_score(tags),
        }
        overall = round(sum(scores.values()) / 3.0, 1)
        return {
            "scores": scores,
            "overall": overall,
            "rating": "excellent" if overall >= 80 else "good" if overall >= 60 else "needs_work",
        }

    def suggest(self, *, title: str, description: str = "", tags: list[str] | None = None) -> dict:
        """Return concrete suggestions to improve a content package."""
        tags = tags or []
        suggestions: list[str] = []
        if len(title) < 30:
            suggestions.append("Title is too short — aim for 30-65 characters with a hook.")
        if len(title) > 90:
            suggestions.append("Title is too long — trim to under 90 characters.")
        if not any(c.isdigit() for c in title):
            suggestions.append("Add a number or specific detail to the title to boost curiosity.")
        if not description:
            suggestions.append("Add a description of at least 20 words with keywords.")
        elif len(description.split()) < 50:
            suggestions.append("Expand the description beyond 50 words with a call to action.")
        if len(tags) < 5:
            suggestions.append("Use at least 5 tags combining broad and niche keywords.")
        if not suggestions:
            suggestions.append("No changes needed — content package looks solid.")
        return {"suggestions": suggestions, "count": len(suggestions)}


_OPTIMIZER: PublisherOptimizer | None = None


def get_publisher_optimizer() -> PublisherOptimizer:
    """Get the module-level singleton optimizer."""
    global _OPTIMIZER
    if _OPTIMIZER is None:
        _OPTIMIZER = PublisherOptimizer()
    return _OPTIMIZER
