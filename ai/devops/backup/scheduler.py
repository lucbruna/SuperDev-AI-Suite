"""Backup scheduler."""
from __future__ import annotations
from typing import Any, Dict, List

class BackupScheduler:
    def __init__(self) -> None:
        self._schedules: Dict[str, Dict[str, Any]] = {}
    def create_schedule(self, name: str, source: str, frequency: str = "daily", retention_days: int = 30) -> Dict[str, Any]:
        schedule = {"name": name, "source": source, "frequency": frequency, "retention_days": retention_days, "enabled": True}
        self._schedules[name] = schedule
        return schedule
    def get_schedule(self, name: str) -> Dict[str, Any]:
        return self._schedules.get(name, {"error": "not_found"})
    def enable(self, name: str) -> bool:
        if name in self._schedules:
            self._schedules[name]["enabled"] = True
            return True
        return False
    def disable(self, name: str) -> bool:
        if name in self._schedules:
            self._schedules[name]["enabled"] = False
            return True
        return False
    def list_schedules(self) -> List[Dict[str, Any]]:
        return list(self._schedules.values())
    def delete_schedule(self, name: str) -> bool:
        if name in self._schedules:
            del self._schedules[name]
            return True
        return False
    def count(self) -> int:
        return len(self._schedules)
