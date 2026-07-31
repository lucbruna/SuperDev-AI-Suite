from __future__ import annotations

from typing import Any


class Indexing:
    """Index structures for efficient long-term memory retrieval."""

    def __init__(self):
        self._keys: dict[str, dict[str, Any]] = {}
        self._tags: dict[str, set[str]] = {}
        self._keywords: dict[str, set[str]] = {}

    @property
    def count(self) -> int:
        return len(self._keys)

    def add(self, key: str, data: dict[str, Any]) -> None:
        self._keys[key] = data
        for _k, v in data.items():
            if isinstance(v, str):
                for word in v.lower().split():
                    if len(word) > 2:
                        self._keywords.setdefault(word, set()).add(key)
        tags = data.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                self._tags.setdefault(str(tag), set()).add(key)

    def remove(self, key: str) -> bool:
        if key not in self._keys:
            return False
        del self._keys[key]
        for word_set in self._keywords.values():
            word_set.discard(key)
        for tag_set in self._tags.values():
            tag_set.discard(key)
        return True

    def search(self, query: str) -> list[str]:
        q = query.lower()
        results: set[str] = set()
        for key in self._keys:
            if q in key.lower():
                results.add(key)
        for word, keys in self._keywords.items():
            if q in word:
                results.update(keys)
        scored = [(key, self._score(key, q)) for key in results]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [k for k, _ in scored]

    def _score(self, key: str, query: str) -> float:
        score = 0.0
        if query in key.lower():
            score += 10.0
        data = self._keys.get(key, {})
        for value in data.values():
            if isinstance(value, str) and query in value.lower():
                score += 1.0
        return score

    def search_by_tag(self, tag: str) -> list[str]:
        return list(self._tags.get(tag, set()))

    def clear(self) -> None:
        self._keys.clear()
        self._tags.clear()
        self._keywords.clear()

    def keys(self) -> list[str]:
        return list(self._keys.keys())
