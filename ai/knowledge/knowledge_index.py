from __future__ import annotations

from typing import Any


class KnowledgeIndex:
    """Index structure for efficient knowledge retrieval."""

    def __init__(self):
        self._entries: dict[str, dict[str, Any]] = {}
        self._tags: dict[str, set[str]] = {}

    @property
    def entries(self) -> dict[str, dict[str, Any]]:
        return {k: dict(v) for k, v in self._entries.items()}

    def add_entry(self, key: str, data: dict[str, Any], tags: list[str] | None = None) -> None:
        self._entries[key] = data
        if tags:
            for tag in tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(key)

    def get_entry(self, key: str) -> dict[str, Any] | None:
        entry = self._entries.get(key)
        return dict(entry) if entry else None

    def remove_entry(self, key: str) -> bool:
        if key not in self._entries:
            return False
        del self._entries[key]
        for tag_keys in self._tags.values():
            tag_keys.discard(key)
        return True

    def update_entry(self, key: str, data: dict[str, Any]) -> bool:
        if key not in self._entries:
            return False
        self._entries[key].update(data)
        return True

    def search(self, query: str) -> list[dict[str, Any]]:
        query_lower = query.lower()
        results: list[dict[str, Any]] = []
        for key, data in self._entries.items():
            if query_lower in key.lower():
                results.append({"key": key, "data": dict(data)})
                continue
            for value in data.values():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append({"key": key, "data": dict(data)})
                    break
        return results

    def search_by_tag(self, tag: str) -> list[dict[str, Any]]:
        keys = self._tags.get(tag, set())
        return [{"key": k, "data": dict(self._entries[k])} for k in keys if k in self._entries]

    def get_tags(self, key: str) -> list[str]:
        return [tag for tag, keys in self._tags.items() if key in keys]

    def add_tag(self, key: str, tag: str) -> None:
        if tag not in self._tags:
            self._tags[tag] = set()
        self._tags[tag].add(key)

    def remove_tag(self, key: str, tag: str) -> bool:
        if tag in self._tags and key in self._tags[tag]:
            self._tags[tag].discard(key)
            return True
        return False

    def size(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()
        self._tags.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": {k: dict(v) for k, v in self._entries.items()},
            "tags": {k: list(v) for k, v in self._tags.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeIndex:
        index = cls()
        for k, v in data.get("entries", {}).items():
            index.add_entry(k, dict(v))
        for tag, keys in data.get("tags", {}).items():
            for key in keys:
                index.add_tag(key, tag)
        return index
