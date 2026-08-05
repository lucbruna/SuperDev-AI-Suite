"""Character builder — construct characters described in prompts."""
from __future__ import annotations

import re
from typing import Any


class CharacterBuilder:
    """Extracts character attributes from a prompt and builds a profile."""

    def build(self, prompt: str) -> dict[str, Any]:
        return {
            "name": self._extract_name(prompt),
            "appearance": self._extract_appearance(prompt),
            "clothing": self._extract_clothing(prompt),
        }

    def _extract_name(self, prompt: str) -> str:
        match = re.search(r"\b(?:named|called)\s+([A-Z][a-z]+)", prompt)
        return match.group(1) if match else "unnamed"

    def _extract_appearance(self, prompt: str) -> str:
        match = re.search(
            r"\b(?:a|an)\s+([a-z]+\s+[a-z]+\s+(?:man|woman|person|boy|girl|character))",
            prompt,
            re.IGNORECASE,
        )
        return match.group(1) if match else "generic"

    def _extract_clothing(self, prompt: str) -> str:
        match = re.search(r"\bwearing\s+([a-z\s]+?)(?:[,.]|$)", prompt, re.IGNORECASE)
        return match.group(1).strip() if match else "default outfit"
