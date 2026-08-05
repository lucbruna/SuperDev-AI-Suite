"""X Hashtags — hashtag suggestions for X (Volume 7)."""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_DEFAULT_TRENDING = ["#tech", "#startup", "#AI", "#marketing"]


class XHashtags:
    """Rank hashtags from content text plus trending defaults."""

    @staticmethod
    def _keywords(text: str) -> list[str]:
        return [
            w.lower() for w in re.findall(r"[A-Za-z0-9]+", text)
            if len(w) > 2 and w.lower() not in {"the", "and", "for", "with", "that", "this", "from"}
        ]

    def generate(self, *, text: str = "", count: int = 5) -> dict:
        """Mix default trending hashtags with content keywords."""
        freq: dict[str, int] = {}
        for word in self._keywords(text):
            freq[word] = freq.get(word, 0) + 1
        keywords = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
        combined = [f"#{w}" for w, _ in keywords]
        for tag in _DEFAULT_TRENDING:
            if tag not in combined:
                combined.append(tag)
        hashtags = combined[:count]
        return {"hashtags": hashtags, "count": len(hashtags)}

    def stats(self) -> dict[str, int]:
        return {"trending_defaults": len(_DEFAULT_TRENDING)}


_HASHTAGS: XHashtags | None = None


def get_x_hashtags() -> XHashtags:
    """Get the module-level singleton hashtag helper."""
    global _HASHTAGS
    if _HASHTAGS is None:
        _HASHTAGS = XHashtags()
    return _HASHTAGS
