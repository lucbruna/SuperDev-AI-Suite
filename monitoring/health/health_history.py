from __future__ import annotations

import json
import os
import time
from typing import Any

from ..monitoring_models import HealthStatus


class HealthHistory:
    """Persistent history of health state transitions."""

    def __init__(self, storage_path: str = "health_history.json") -> None:
        self._path = storage_path
        self._entries: list[dict[str, Any]] = []
        self._load()

    def record(self, component: str, status: HealthStatus, message: str = "") -> None:
        self._entries.append({
            "timestamp": time.time(),
            "component": component,
            "status": status.value,
            "message": message,
        })
        self._prune()
        self._save()

    def query(
        self,
        component: str = "",
        status: str = "",
        start_time: float = 0.0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        results = list(self._entries)
        if component:
            results = [e for e in results if e["component"] == component]
        if status:
            results = [e for e in results if e["status"] == status]
        if start_time:
            results = [e for e in results if e["timestamp"] >= start_time]
        results.sort(key=lambda e: e["timestamp"], reverse=True)
        return results[:limit]

    def get_transitions(self, component: str) -> list[dict[str, Any]]:
        entries = self.query(component=component)
        transitions: list[dict[str, Any]] = []
        prev_status = ""
        for entry in reversed(entries):
            if entry["status"] != prev_status:
                transitions.append(entry)
                prev_status = entry["status"]
        return transitions

    def latest(self) -> dict[str, Any]:
        return self._entries[-1] if self._entries else {}

    def _prune(self) -> None:
        max_entries = 10000
        if len(self._entries) > max_entries:
            self._entries = self._entries[-max_entries:]

    def _save(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._entries, f, indent=2, default=str)
        except OSError:
            pass

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                self._entries = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    def clear(self) -> None:
        self._entries.clear()
        self._save()
