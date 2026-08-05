"""Screenwriter engine — coordinates script generation and review."""
from __future__ import annotations

from typing import Any


class ScreenwriterEngine:
    """High-level script generation pipeline."""

    def __init__(self) -> None:
        from modules.ai_video_studio.ai_screenwriter.generators.script_generator import get_script_generator
        from modules.ai_video_studio.ai_screenwriter.generators.hook_generator import get_hook_generator
        from modules.ai_video_studio.ai_screenwriter.generators.title_generator import get_title_generator
        from modules.ai_video_studio.ai_screenwriter.review.script_reviewer import get_script_reviewer
        from modules.ai_video_studio.ai_screenwriter.screenwriter_optimizer import get_screenwriter_optimizer

        self.script_generator = get_script_generator()
        self.hook_generator = get_hook_generator()
        self.title_generator = get_title_generator()
        self.reviewer = get_script_reviewer()
        self.optimizer = get_screenwriter_optimizer()

    def write(self, brief: str, topic: str = "", tone: str = "informative", duration: float = 30.0) -> dict[str, Any]:
        """Generate a full script from a brief."""
        title = self.title_generator.generate(topic or brief)
        hook = self.hook_generator.generate(brief)
        script = self.script_generator.generate(brief, tone=tone, duration=duration)
        review = self.reviewer.review(script)
        optimized = self.optimizer.optimize(script, review)
        return {
            "title": title,
            "hook": hook,
            "script": optimized,
            "review": review,
            "tone": tone,
            "duration": duration,
        }


_screenwriter_engine: ScreenwriterEngine | None = None


def get_screenwriter_engine() -> ScreenwriterEngine:
    global _screenwriter_engine
    if _screenwriter_engine is None:
        _screenwriter_engine = ScreenwriterEngine()
    return _screenwriter_engine
