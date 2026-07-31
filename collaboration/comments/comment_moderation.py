"""Comment moderation."""

from __future__ import annotations

from typing import Any

BLOCKED_WORDS = ("spam", "flood")


def sanitize_body(body: str, max_length: int = 2000) -> str:
    """Collapses whitespace and limits length (mirrors security.sanitize)."""
    cleaned = " ".join(str(body or "").split())
    return cleaned[:max_length]


class CommentModeration:
    """Checks comments before they are published."""

    def __init__(self, blocked_words: list[str] | None = None) -> None:
        self.blocked_words = blocked_words or list(BLOCKED_WORDS)

    def sanitize(self, body: str) -> str:
        return sanitize_body(body)

    def is_blocked(self, body: str) -> bool:
        lowered = body.lower()
        return any(word in lowered for word in self.blocked_words)

    def moderate(self, body: str) -> dict[str, Any]:
        clean = self.sanitize(body)
        blocked = self.is_blocked(clean)
        return {"body": clean, "blocked": blocked,
                "approved": not blocked}
