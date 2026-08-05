"""Metric history: a time-series store of graph snapshots.

The intelligence engine appends a snapshot (graph stats + key metrics +
timestamp) after each analysis; trend and forecast logic consume the series.
Storage is a single JSON file for zero dependencies.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any


class MetricHistory:
    """Bounded append-only series of metric snapshots."""

    def __init__(self, path: str, limit: int = 500) -> None:
        self.path = path
        self.limit = max(limit, 10)
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ io
    def load(self) -> list[dict[str, Any]]:
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                return data[-self.limit :]
        except (OSError, ValueError):
            pass
        return []

    def save(self, snapshots: list[dict[str, Any]]) -> None:
        path = Path(self.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(snapshots[-self.limit :], handle, ensure_ascii=False)
        tmp.replace(path)

    # --------------------------------------------------------------- append
    def append(self, snapshot: dict[str, Any], *, min_interval_seconds: int = 0) -> bool:
        """Append a snapshot if enough time passed since the last one.

        Returns True when appended, False when throttled (too soon).
        """
        with self._lock:
            series = self.load()
            if series and min_interval_seconds > 0:
                last_ts = series[-1].get("ts", 0)
                if time.time() - last_ts < min_interval_seconds:
                    return False
            series.append(snapshot)
            self.save(series)
            return True

    # --------------------------------------------------------------- reads
    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.load()[-limit:]

    def series(
        self, key: str, *, limit: int | None = None
    ) -> tuple[list[float], list[float]]:
        """Return (timestamps, values) for a numeric metric key."""
        timestamps: list[float] = []
        values: list[float] = []
        snapshots = self.load()
        if limit:
            snapshots = snapshots[-limit:]
        for snap in snapshots:
            value = _dig(snap, key)
            if value is not None:
                timestamps.append(float(snap.get("ts", 0)))
                values.append(float(value))
        return timestamps, values

    def count(self) -> int:
        return len(self.load())


def _dig(payload: dict[str, Any], dotted: str) -> Any:
    node: Any = payload
    for part in dotted.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def get_history() -> MetricHistory:
    """Convenience: history bound to the process-wide settings."""
    from modules.architecture_intelligence.config.intelligence_settings import (
        get_settings,
    )

    settings = get_settings()
    settings.ensure_dirs()
    return MetricHistory(settings.history_path, settings.config.history_limit)
