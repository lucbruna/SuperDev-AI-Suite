from __future__ import annotations

from typing import Any


class KnowledgeMerger:
    """Merges overlapping or complementary knowledge entries."""

    def __init__(self):
        self._merges: int = 0

    @property
    def merge_count(self) -> int:
        return self._merges

    def merge(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not entries:
            return []
        merged: dict[str, dict[str, Any]] = {}
        for entry in entries:
            key = entry.get("topic", entry.get("type", "unknown"))
            if key in merged:
                existing = merged[key]
                existing["sources"] = list(set(existing.get("sources", [])) | {entry.get("id", "?")})
                existing["merge_count"] = existing.get("merge_count", 1) + 1
                content = existing.get("content", {})
                if isinstance(content, dict) and isinstance(entry.get("content"), dict):
                    content.update(entry["content"])
                self._merges += 1
            else:
                merged[key] = dict(entry)
                merged[key]["sources"] = [entry.get("id", "?")]
                merged[key]["merge_count"] = 1
        return list(merged.values())

    def merge_by_key(self, entries: list[dict[str, Any]], merge_key: str) -> list[dict[str, Any]]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for entry in entries:
            k = str(entry.get(merge_key, "unknown"))
            groups.setdefault(k, []).append(entry)
        result: list[dict[str, Any]] = []
        for _key, group in groups.items():
            if len(group) == 1:
                result.append(group[0])
            else:
                base = dict(group[0])
                base["_merged_from"] = [e.get("id", "?") for e in group]
                base["_merge_count"] = len(group)
                content = base.get("content", {})
                if isinstance(content, dict):
                    for e in group[1:]:
                        if isinstance(e.get("content"), dict):
                            content.update(e["content"])
                result.append(base)
                self._merges += len(group) - 1
        return result

    def reset(self) -> None:
        self._merges = 0
