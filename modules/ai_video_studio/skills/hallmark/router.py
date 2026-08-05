"""Hallmark router — keyword-based routing to a category."""
from __future__ import annotations
from typing import Any


class SkillRouter:
    """Route a task description to the best-matching skill category."""

    _KEYWORDS: dict[str, tuple[str, ...]] = {
        "video": ("video", "film", "youtube", "tiktok", "documentary", "ad"),
        "voice": ("voice", "audio", "narration", "podcast", "dubbing"),
        "marketing": ("marketing", "ad copy", "seo", "campaign", "brand"),
        "business": ("pitch", "plan", "proposal", "contract", "report"),
        "development": ("code", "test", "api", "debug", "refactor", "documentation"),
        "security": ("security", "vulnerability", "secrets", "audit", "policy"),
        "workflow": ("workflow", "schedule", "approval", "backup", "version"),
        "ai": ("prompt", "model", "llm", "rag", "agent", "pipeline"),
        "general": (),
    }

    def route(self, task: str, *categories: str) -> str:
        """Return the category with the most keyword hits (default 'general')."""
        lowered = task.lower()
        best, best_score = "general", 0
        for category in categories:
            score = sum(1 for keyword in self._KEYWORDS.get(category, ()) if keyword in lowered)
            if score > best_score:
                best, best_score = category, score
        return best
