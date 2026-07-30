from __future__ import annotations

import re
from typing import Any


class ContentModerator:
    """Moderates LLM content using pattern matching."""

    _DEFAULT_PATTERNS: dict[str, list[str]] = {
        "toxicity": [
            r"(?i)\b(hate|kill|die|stupid|idiot)\b",
        ],
        "hate": [
            r"(?i)\b(nigger|faggot|retard)\b",
        ],
        "sexual": [
            r"(?i)\b(porn|sex|nsfw)\b",
        ],
        "violence": [
            r"(?i)\b(shoot|bomb|attack|murder)\b",
        ],
    }

    def __init__(self) -> None:
        self._patterns: dict[str, list[re.Pattern]] = {}
        for category, pat_strs in self._DEFAULT_PATTERNS.items():
            self._patterns[category] = [re.compile(p) for p in pat_strs]

    def add_pattern(self, category: str, pattern: str) -> None:
        if category not in self._patterns:
            self._patterns[category] = []
        self._patterns[category].append(re.compile(pattern, re.IGNORECASE))

    def check_text(self, text: str) -> dict[str, Any]:
        if not text:
            return {"flagged": False, "categories": {}, "scores": {}}

        flagged = False
        categories: dict[str, bool] = {}
        scores: dict[str, float] = {}

        for category, patterns in self._patterns.items():
            category_flagged = False
            total_hits = 0
            for pat in patterns:
                hits = len(pat.findall(text))
                total_hits += hits
                if hits > 0:
                    category_flagged = True

            categories[category] = category_flagged
            scores[category] = min(1.0, total_hits / 10.0)
            if category_flagged:
                flagged = True

        return {
            "flagged": flagged,
            "categories": categories,
            "scores": scores,
            "text_length": len(text),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "categories": list(self._patterns.keys()),
            "total_categories": len(self._patterns),
            "total_patterns": sum(len(p) for p in self._patterns.values()),
        }
