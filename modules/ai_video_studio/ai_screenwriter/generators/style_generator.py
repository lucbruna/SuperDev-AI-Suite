"""Style generator — selects writing style parameters."""
from __future__ import annotations

from typing import Any

STYLES = {
    "conversational": {"sentence_length": "short", "vocabulary": "simple"},
    "professional": {"sentence_length": "medium", "vocabulary": "formal"},
    "dramatic": {"sentence_length": "long", "vocabulary": "emotional"},
    "minimalist": {"sentence_length": "very short", "vocabulary": "essential"},
}


class StyleGenerator:
    """Generates style parameters for the script."""

    def generate(self, style: str = "conversational") -> dict[str, Any]:
        return {"style": style, **STYLES.get(style, STYLES["conversational"])}


_style_generator: StyleGenerator | None = None


def get_style_generator() -> StyleGenerator:
    global _style_generator
    if _style_generator is None:
        _style_generator = StyleGenerator()
    return _style_generator
