"""Prompt engine — orchestrates classification, rewrite, expand, optimize."""
from __future__ import annotations

from typing import Any


class PromptEngine:
    """High-level prompt pipeline: classify -> rewrite -> expand -> optimize."""

    def __init__(self) -> None:
        from modules.ai_video_studio.ai_prompt_engine.prompt_classifier import get_prompt_classifier
        from modules.ai_video_studio.ai_prompt_engine.prompt_rewriter import get_prompt_rewriter
        from modules.ai_video_studio.ai_prompt_engine.prompt_expander import get_prompt_expander
        from modules.ai_video_studio.ai_prompt_engine.prompt_optimizer import get_prompt_optimizer
        from modules.ai_video_studio.ai_prompt_engine.prompt_validator import get_prompt_validator
        from modules.ai_video_studio.ai_prompt_engine.prompt_cache import get_prompt_cache

        self.classifier = get_prompt_classifier()
        self.rewriter = get_prompt_rewriter()
        self.expander = get_prompt_expander()
        self.optimizer = get_prompt_optimizer()
        self.validator = get_prompt_validator()
        self.cache = get_prompt_cache()

    def process(self, prompt: str, *, style: str | None = None, expand: bool = True) -> dict[str, Any]:
        """Run the full prompt pipeline and return a structured result."""
        cached = self.cache.get(prompt)
        if cached is not None:
            return cached

        validation = self.validator.validate(prompt)
        if not validation["valid"]:
            return {"prompt": prompt, "valid": False, "issues": validation["issues"], "pipeline": "rejected"}

        classification = self.classifier.classify(prompt)
        rewritten = self.rewriter.rewrite(prompt)
        optimized = self.optimizer.optimize(rewritten["rewritten"], style=style)
        expanded = self.expander.expand(optimized["optimized"]) if expand else None

        result = {
            "prompt": prompt,
            "valid": True,
            "classification": classification,
            "rewritten": rewritten["rewritten"],
            "optimized": optimized["optimized"],
            "expanded": expanded["expanded"] if expanded else None,
            "score": optimized["score"],
            "pipeline": "complete",
        }
        self.cache.set(prompt, result)
        return result

    def ready_to_generate(self, prompt: str, *, min_score: int = 40) -> bool:
        result = self.process(prompt, expand=False)
        return result.get("valid", False) and result.get("score", 0) >= min_score


_prompt_engine: PromptEngine | None = None


def get_prompt_engine() -> PromptEngine:
    global _prompt_engine
    if _prompt_engine is None:
        _prompt_engine = PromptEngine()
    return _prompt_engine
