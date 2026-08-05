"""Prompt optimizer — improve prompt quality through heuristics."""
from __future__ import annotations

from typing import Any


class PromptOptimizer:
    """Optimizes prompts: adds structure, specificity and action verbs."""

    def optimize(self, prompt: str, style: str | None = None) -> dict[str, Any]:
        text = (prompt or "").strip().rstrip(".")
        if not text:
            return {"original": prompt, "optimized": "", "improvements": []}

        improvements: list[str] = []
        optimized = text

        # Ensure an action verb lead-in for video briefs. Covers infinitive and
        # imperative forms (pt/en) so prompts already starting with an action
        # verb are not double-prefixed.
        _action_verbs = (
            "criar", "crie", "cria", "fazer", "faça", "faca", "faz", "gera",
            "gerar", "gere", "produzir", "produza", "produz", "montar", "monte",
            "create", "make", "generate", "produce", "build", "craft",
        )
        if not any(optimized.lower().startswith(v) for v in _action_verbs):
            optimized = f"Create a video about {optimized}"
            improvements.append("added_action_verb")

        # Append style guidance.
        if style:
            optimized += f" with a {style} visual style."
            improvements.append("added_style")

        # Append output expectation.
        if "video" not in optimized.lower():
            optimized += " Deliver a complete video."
            improvements.append("added_output_expectation")

        return {
            "original": prompt,
            "optimized": optimized,
            "improvements": improvements,
            "score": self.score(optimized),
        }

    @staticmethod
    def score(prompt: str) -> int:
        """0-100 heuristic quality score."""
        text = (prompt or "").lower()
        score = 20
        if len(text.split()) >= 5:
            score += 20
        if any(k in text for k in ("about", "sobre", "sobre a", "for", "para")):
            score += 20
        if any(k in text for k in ("video", "vídeo")):
            score += 20
        if len(text) >= 40:
            score += 20
        return min(score, 100)


_prompt_optimizer: PromptOptimizer | None = None


def get_prompt_optimizer() -> PromptOptimizer:
    global _prompt_optimizer
    if _prompt_optimizer is None:
        _prompt_optimizer = PromptOptimizer()
    return _prompt_optimizer
