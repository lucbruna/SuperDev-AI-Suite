"""Consistency engine — enforce temporal/character consistency."""
from __future__ import annotations

from typing import Any


class ConsistencyEngine:
    """Checks that characters and scenes stay consistent across frames."""

    def __init__(self) -> None:
        self._references: dict[str, dict[str, Any]] = {}

    def register_reference(self, key: str, descriptor: dict[str, Any]) -> None:
        self._references[key] = descriptor

    def check(self, frames: list[dict[str, Any]]) -> dict[str, Any]:
        if len(frames) < 2:
            return {"consistent": True, "drift_count": 0, "notes": ["too few frames"]}
        drift = 0
        notes: list[str] = []
        reference_seed = frames[0].get("seed")
        for frame in frames[1:]:
            if frame.get("seed") != reference_seed:
                drift += 1
                notes.append(f"frame {frame['index']} drifted from reference seed")
        return {"consistent": drift == 0, "drift_count": drift, "notes": notes}
