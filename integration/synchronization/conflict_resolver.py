"""Conflict resolution strategies for bidirectional sync."""

from __future__ import annotations

from typing import Any

_STRATEGIES = {"source", "target", "newest", "merge"}


class ConflictResolver:
    """Resolves conflicting records between source and target."""

    def __init__(self, strategy: str = "newest") -> None:
        if strategy not in _STRATEGIES:
            raise ValueError(f"unknown strategy {strategy!r}")
        self.strategy = strategy

    def resolve(self, source: dict[str, Any], target: dict[str, Any],
                strategy: str | None = None) -> dict[str, Any]:
        chosen = strategy or self.strategy
        if chosen == "source":
            return dict(source)
        if chosen == "target":
            return dict(target)
        if chosen == "merge":
            merged = dict(target)
            merged.update({k: v for k, v in source.items() if v is not None})
            return merged
        # newest: compare timestamps
        s_ts = source.get("updated_at", source.get("timestamp", 0))
        t_ts = target.get("updated_at", target.get("timestamp", 0))
        return dict(source) if s_ts >= t_ts else dict(target)

    def strategies(self) -> list[str]:
        return sorted(_STRATEGIES)
