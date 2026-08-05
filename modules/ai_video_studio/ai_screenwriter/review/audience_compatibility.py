"""Audience compatibility — matches script against target audience profile."""
from __future__ import annotations

from typing import Any


class AudienceCompatibility:
    """Scores how well a script fits an audience segment."""

    def evaluate(self, script: dict[str, Any], audience: str = "general") -> dict[str, Any]:
        text = script.get("text", "")
        lowered = text.lower()
        keywords = {
            "beginners": ("básico", "primeiro", "simples", "iniciante"),
            "experts": ("avançado", "profundo", "complexo", "performance"),
            "general": ("como", "guia", "dica", "passo"),
        }
        hits = sum(1 for word in keywords.get(audience, keywords["general"]) if word in lowered)
        score = 0.4 + 0.15 * hits
        return {
            "audience": audience,
            "score": round(max(0.0, min(1.0, score)), 3),
            "compatible": score >= 0.7,
        }


_audience_compatibility: AudienceCompatibility | None = None


def get_audience_compatibility() -> AudienceCompatibility:
    global _audience_compatibility
    if _audience_compatibility is None:
        _audience_compatibility = AudienceCompatibility()
    return _audience_compatibility
