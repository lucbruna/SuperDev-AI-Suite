"""Data retention policies."""

from __future__ import annotations

import time
import uuid
from typing import Any


class RetentionRule:
    def __init__(self, data_type: str, retention_days: int, action: str = "delete", description: str = "") -> None:
        self.rule_id = str(uuid.uuid4())[:8]
        self.data_type = data_type
        self.retention_days = retention_days
        self.action = action
        self.description = description
        self.enabled = True


class DataRetention:
    def __init__(self) -> None:
        self._rules: dict[str, RetentionRule] = {}
        self._data_entries: dict[str, dict[str, Any]] = {}
        self._deletion_log: list[dict[str, Any]] = []

    def add_rule(
        self, data_type: str, retention_days: int, action: str = "delete", description: str = ""
    ) -> RetentionRule:
        rule = RetentionRule(data_type, retention_days, action, description)
        self._rules[rule.rule_id] = rule
        return rule

    def register_data(self, data_id: str, data_type: str, created_at: float = 0.0) -> None:
        self._data_entries[data_id] = {"type": data_type, "created_at": created_at or time.time()}

    def check_expired(self) -> list[str]:
        expired = []
        for data_id, data in self._data_entries.items():
            rule = self._find_rule(data["type"])
            if rule and rule.enabled:
                age_days = (time.time() - data["created_at"]) / 86400
                if age_days > rule.retention_days:
                    expired.append(data_id)
        return expired

    def _find_rule(self, data_type: str) -> RetentionRule | None:
        for rule in self._rules.values():
            if rule.data_type == data_type:
                return rule
        return None

    def enforce_retention(self) -> list[str]:
        expired = self.check_expired()
        for data_id in expired:
            data = self._data_entries.pop(data_id, None)
            if data:
                self._deletion_log.append({"data_id": data_id, "type": data["type"], "deleted_at": time.time()})
        return expired

    def get_rules(self) -> list[dict[str, Any]]:
        return [
            {
                "id": r.rule_id,
                "type": r.data_type,
                "retention_days": r.retention_days,
                "action": r.action,
                "enabled": r.enabled,
            }
            for r in self._rules.values()
        ]

    def get_deletion_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._deletion_log[-limit:]

    def list_data_types(self) -> list[str]:
        return list(set(d["type"] for d in self._data_entries.values()))
