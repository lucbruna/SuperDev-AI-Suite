"""Prompt rewriter — rewrite prompts for clarity and specificity."""
from __future__ import annotations

import re
from typing import Any

STOPWORDS = {
    "de", "da", "do", "dos", "das", "e", "ou", "um", "uma", "para", "com", "sobre",
    "em", "no", "na", "por", "que", "the", "a", "an", "of", "and", "for", "with",
}


class PromptRewriter:
    """Deterministic prompt rewriting: normalize, expand shorthand, clean up."""

    def rewrite(self, prompt: str) -> dict[str, Any]:
        text = (prompt or "").strip()
        original = text

        # Normalize whitespace and casing of acronyms.
        text = re.sub(r"\s+", " ", text)
        text = text[:1].upper() + text[1:] if text else text
        if not text.endswith((".", "?", "!")):
            text += "."

        tokens = text.split()
        keywords = [t for t in tokens if t.strip(".,;:!?()").lower() not in STOPWORDS]

        changes = []
        if text != original:
            changes.append("normalized_whitespace")
        if keywords and len(keywords) < 3:
            text = self._expand_short(text)
            changes.append("expanded_short")

        return {
            "rewritten": text,
            "original": original,
            "changes": changes,
            "keyword_count": len(keywords),
        }

    @staticmethod
    def _expand_short(text: str) -> str:
        """Expand terse prompts into a fuller video brief."""
        t = text.strip().rstrip(".")
        if len(t.split()) < 3:
            return f"Create a video about {t.lower()}, covering the main topics with clear visuals and narration."
        return text

    def rewrite_for_video(self, prompt: str, style: str = "cinematic") -> str:
        result = self.rewrite(prompt)
        return f"{result['rewritten']} Style: {style}."


_prompt_rewriter: PromptRewriter | None = None


def get_prompt_rewriter() -> PromptRewriter:
    global _prompt_rewriter
    if _prompt_rewriter is None:
        _prompt_rewriter = PromptRewriter()
    return _prompt_rewriter
