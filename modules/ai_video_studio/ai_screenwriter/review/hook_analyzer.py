"""Hook analyzer — evaluates the strength of the opening hook."""
from __future__ import annotations

from typing import Any


class HookAnalyzer:
    """Scores hooks based on curiosity-driven patterns."""

    def analyze(self, hook: str) -> dict[str, Any]:
        lowered = hook.lower()
        score = 0.5
        if any(word in lowered for word in ("você sabia", "segredo", "nunca", "por que", "como")):
            score += 0.3
        if len(hook) > 80:
            score -= 0.2
        return {"score": round(max(0.0, min(1.0, score)), 3), "strong": score >= 0.7}


_hook_analyzer: HookAnalyzer | None = None


def get_hook_analyzer() -> HookAnalyzer:
    global _hook_analyzer
    if _hook_analyzer is None:
        _hook_analyzer = HookAnalyzer()
    return _hook_analyzer
