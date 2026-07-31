from __future__ import annotations

from typing import Any


class Abstraction:
    """Creates higher-level abstractions from concrete memory entries."""

    def __init__(self):
        self._abstractions: list[dict[str, Any]] = []
        self._abstraction_count: int = 0

    @property
    def abstractions(self) -> list[dict[str, Any]]:
        return list(self._abstractions)

    @property
    def abstraction_count(self) -> int:
        return self._abstraction_count

    def create_abstractions(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        type_groups: dict[str, list[dict[str, Any]]] = {}
        for entry in entries:
            t = entry.get("type", "unknown")
            type_groups.setdefault(t, []).append(entry)
        for t, group in type_groups.items():
            abstract: dict[str, Any] = {
                "type": t,
                "abstract": True,
                "instance_count": len(group),
                "common_keys": list(set().union(*(e.keys() for e in group))),
                "summary": self._abstract_summary(group),
            }
            result.append(abstract)
            self._abstractions.append(abstract)
            self._abstraction_count += 1
        return result

    def _abstract_summary(self, entries: list[dict[str, Any]]) -> str:
        if not entries:
            return ""
        contents = [str(e.get("content", ""))[:50] for e in entries if e.get("content")]
        if not contents:
            return "No content"
        return f"Abstraction of {len(entries)} items: {contents[0]}..."

    def merge_abstractions(self, abstractions: list[dict[str, Any]]) -> dict[str, Any]:
        if not abstractions:
            return {"abstract": True, "instance_count": 0}
        merged: dict[str, Any] = {
            "abstract": True,
            "instance_count": sum(a.get("instance_count", 0) for a in abstractions),
            "types": list({a.get("type", "?") for a in abstractions}),
        }
        self._abstractions.append(merged)
        self._abstraction_count += 1
        return merged

    def clear(self) -> None:
        self._abstractions.clear()
        self._abstraction_count = 0
