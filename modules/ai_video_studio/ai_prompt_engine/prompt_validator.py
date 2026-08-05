"""Prompt validator — validate prompt length, structure and completeness."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

MIN_LENGTH = 3
MAX_LENGTH = 5000


class PromptValidator:
    """Validates prompts and returns structured issues."""

    def validate(self, prompt: str) -> dict[str, Any]:
        issues: list[str] = []
        text = (prompt or "").strip()
        if not text:
            issues.append("Prompt is empty")
        elif len(text) < MIN_LENGTH:
            issues.append(f"Prompt too short (min {MIN_LENGTH} chars)")
        if len(text) > MAX_LENGTH:
            issues.append(f"Prompt too long (max {MAX_LENGTH} chars)")
        if text and not any(ch.isalpha() for ch in text):
            issues.append("Prompt has no alphabetic characters")
        return {
            "valid": not issues,
            "issues": issues,
            "length": len(text),
            "word_count": len(text.split()),
        }

    def assert_valid(self, prompt: str) -> None:
        result = self.validate(prompt)
        if not result["valid"]:
            raise ValidationError("; ".join(result["issues"]), field="prompt")


_prompt_validator: PromptValidator | None = None


def get_prompt_validator() -> PromptValidator:
    global _prompt_validator
    if _prompt_validator is None:
        _prompt_validator = PromptValidator()
    return _prompt_validator
