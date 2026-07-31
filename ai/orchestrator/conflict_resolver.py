from __future__ import annotations

from typing import Any


class ConflictResolver:
    def __init__(self):
        self._strategies = {
            "last_write_wins": self._last_write_wins,
            "first_write_wins": self._first_write_wins,
            "merge": self._merge,
            "majority": self._majority,
        }

    async def resolve(self, key: str, entries: list[dict[str, Any]], strategy: str = "last_write_wins") -> Any:
        resolver = self._strategies.get(strategy, self._last_write_wins)
        return await resolver(entries)

    async def _last_write_wins(self, entries: list[dict[str, Any]]) -> Any:
        if not entries:
            return None
        latest = max(entries, key=lambda e: e.get("timestamp", 0))
        return latest.get("value")

    async def _first_write_wins(self, entries: list[dict[str, Any]]) -> Any:
        if not entries:
            return None
        earliest = min(entries, key=lambda e: e.get("timestamp", 0))
        return earliest.get("value")

    async def _merge(self, entries: list[dict[str, Any]]) -> Any:
        if not entries:
            return None
        merged: dict[str, Any] = {}
        for entry in entries:
            value = entry.get("value", {})
            if isinstance(value, dict):
                merged.update(value)
            elif isinstance(value, list):
                for item in value:
                    if item not in merged.get("_list", []):
                        merged.setdefault("_list", []).append(item)
            else:
                return entries[-1].get("value")
        return merged

    async def _majority(self, entries: list[dict[str, Any]]) -> Any:
        if not entries:
            return None
        from collections import Counter

        values = [str(e.get("value")) for e in entries]
        counter = Counter(values)
        most_common = counter.most_common(1)
        if most_common:
            for e in entries:
                if str(e.get("value")) == most_common[0][0]:
                    return e["value"]
        return entries[0].get("value")

    async def detect_conflicts(
        self, key: str, entries: list[dict[str, Any]], threshold: float = 5.0
    ) -> list[dict[str, Any]]:
        if len(entries) < 2:
            return []
        values = [e.get("value") for e in entries]
        unique = set(str(v) for v in values)
        if len(unique) <= 1:
            return []
        conflicts = []
        for i, e1 in enumerate(entries):
            for j, e2 in enumerate(entries):
                if i < j and str(e1.get("value")) != str(e2.get("value")):
                    time_diff = abs(e1.get("timestamp", 0) - e2.get("timestamp", 0))
                    conflicts.append(
                        {
                            "key": key,
                            "agent_a": e1.get("agent_id"),
                            "agent_b": e2.get("agent_id"),
                            "value_a": e1.get("value"),
                            "value_b": e2.get("value"),
                            "time_diff": time_diff,
                        }
                    )
        return conflicts[:10]
