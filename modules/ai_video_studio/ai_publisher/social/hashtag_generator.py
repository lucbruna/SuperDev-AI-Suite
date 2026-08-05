"""Hashtag Generator — trending + relevance-based hashtag suggestion (Volume 7)."""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_STOPWORDS = {"o", "a", "os", "as", "de", "do", "da", "em", "para", "com", "um", "uma", "e", "ou", "no", "na"}


class HashtagGenerator:
    """Generate ranked hashtags from content text and optional seed tags."""

    @staticmethod
    def _words(text: str) -> list[str]:
        return [
            w.lower()
            for w in re.findall(r"[A-Za-zÀ-ÿ0-9]+", text)
            if w.lower() not in _STOPWORDS and len(w) > 2
        ]

    def generate(self, *, text: str, seed_tags: list[str] | None = None, count: int = 10) -> dict:
        """Return ranked hashtags mixing seed tags with content keywords."""
        seeds = [t.lstrip("#").lower() for t in (seed_tags or [])]
        freq: dict[str, int] = {}
        for word in self._words(text):
            freq[word] = freq.get(word, 0) + 1
        keywords = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
        combined: list[str] = []
        for word, _n in keywords:
            if word not in combined:
                combined.append(word)
        for tag in seeds:
            if tag not in combined:
                combined.append(tag)
        tags = combined[:count]
        return {
            "hashtags": [f"#{t}" for t in tags],
            "count": len(tags),
            "source": "content+seeds" if seeds else "content",
        }

    def stats(self) -> dict[str, int]:
        return {"max_hashtags": 30}


_GENERATOR: HashtagGenerator | None = None


def get_hashtag_generator() -> HashtagGenerator:
    """Get the module-level singleton hashtag generator."""
    global _GENERATOR
    if _GENERATOR is None:
        _GENERATOR = HashtagGenerator()
    return _GENERATOR
