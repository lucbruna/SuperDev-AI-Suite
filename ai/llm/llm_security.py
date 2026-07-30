from __future__ import annotations

import re
from typing import Any

from .llm_interfaces import ILLMSecurity


class LLMSecurity(ILLMSecurity):
    """Security and moderation for LLM operations."""

    def __init__(self) -> None:
        self._blocked_patterns: list[re.Pattern] = []
        self._allowed_patterns: list[re.Pattern] = []

    def add_blocked_pattern(self, pattern: str) -> None:
        self._blocked_patterns.append(re.compile(pattern, re.IGNORECASE))

    def add_allowed_pattern(self, pattern: str) -> None:
        self._allowed_patterns.append(re.compile(pattern, re.IGNORECASE))

    async def validate_prompt(self, prompt: str) -> dict[str, Any]:
        issues: list[str] = []

        for pattern in self._blocked_patterns:
            if pattern.search(prompt):
                issues.append(f"Blocked pattern detected: {pattern.pattern}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "prompt_length": len(prompt),
        }

    async def validate_output(self, output: str) -> dict[str, Any]:
        issues: list[str] = []

        if not output.strip():
            issues.append("Empty output")

        for pattern in self._blocked_patterns:
            if pattern.search(output):
                issues.append(f"Blocked pattern in output: {pattern.pattern}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "output_length": len(output),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocked_patterns": [p.pattern for p in self._blocked_patterns],
            "allowed_patterns": [p.pattern for p in self._allowed_patterns],
        }
