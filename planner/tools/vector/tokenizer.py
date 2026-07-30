from __future__ import annotations

from typing import Any


class Tokenizer:
    """Simple tokenizer with count and truncation utilities."""

    def __init__(self, model: str = "default"):
        self.model = model

    def count_tokens(self, text: str) -> int:
        """Approximate token count (4 chars per token)."""
        return (len(text) + 3) // 4

    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within max_tokens."""
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3] + "..." if max_chars > 3 else text[:max_chars]

    def encode(self, text: str) -> list[int]:
        """Encode text to token IDs (character-level stub)."""
        return [ord(c) for c in text]

    def decode(self, token_ids: list[int]) -> str:
        """Decode token IDs back to text."""
        return "".join(chr(t) for t in token_ids if 0 <= t <= 0x10FFFF)
