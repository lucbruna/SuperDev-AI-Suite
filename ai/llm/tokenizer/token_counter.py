from __future__ import annotations

from typing import Any


class TokenCounter:
    """Simple token counter using character-length approximation."""

    CHARS_PER_TOKEN = 4

    def count(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // self.CHARS_PER_TOKEN + 1)

    def count_messages(self, messages: list[dict[str, Any]]) -> int:
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += self.count(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        total += self.count(part.get("text", ""))
        return total

    def truncate(self, text: str, max_tokens: int) -> str:
        max_chars = max_tokens * self.CHARS_PER_TOKEN
        if len(text) <= max_chars:
            return text
        return text[:max_chars]

    def to_dict(self) -> dict[str, Any]:
        return {
            "chars_per_token": self.CHARS_PER_TOKEN,
        }
