from __future__ import annotations

from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any


class RetentionPeriod(Enum):
    DAYS_7 = 7
    DAYS_30 = 30
    DAYS_90 = 90
    YEAR_1 = 365
    YEAR_3 = 1095
    FOREVER = -1


class AccessLevel(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


class AuditPolicy:
    def __init__(self, name: str, retention: RetentionPeriod, access: AccessLevel, max_entries: int = 10000):
        self.name = name
        self.retention = retention
        self.access = access
        self.max_entries = max_entries

    def should_archive(self, entry_timestamp: str) -> bool:
        if self.retention == RetentionPeriod.FOREVER:
            return False
        try:
            entry_time = datetime.fromisoformat(entry_timestamp)
            cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention.value)
            return entry_time < cutoff
        except (ValueError, TypeError):
            return False

    def can_access(self, user_role: str) -> bool:
        role_levels = {"admin": "confidential", "manager": "restricted", "developer": "internal", "viewer": "public"}
        user_access = role_levels.get(user_role, "public")
        level_order = ["public", "internal", "restricted", "confidential"]
        return level_order.index(user_access) >= level_order.index(self.access.value)


class PolicyManager:
    def __init__(self):
        self._policies: dict[str, AuditPolicy] = {
            "default": AuditPolicy("default", RetentionPeriod.DAYS_90, AccessLevel.INTERNAL),
            "security": AuditPolicy("security", RetentionPeriod.YEAR_1, AccessLevel.RESTRICTED),
            "compliance": AuditPolicy("compliance", RetentionPeriod.YEAR_3, AccessLevel.CONFIDENTIAL),
            "user_activity": AuditPolicy("user_activity", RetentionPeriod.DAYS_30, AccessLevel.INTERNAL),
        }

    def get_policy(self, name: str) -> AuditPolicy:
        return self._policies.get(name, self._policies["default"])

    def set_policy(self, name: str, policy: AuditPolicy):
        self._policies[name] = policy

    def list_policies(self) -> list[dict[str, Any]]:
        return [{"name": p.name, "retention": p.retention.name, "access": p.access.value, "max_entries": p.max_entries} for p in self._policies.values()]

    def entries_to_archive(self, entries: list[dict[str, Any]], policy_name: str = "default") -> list[dict[str, Any]]:
        policy = self.get_policy(policy_name)
        return [e for e in entries if policy.should_archive(e.get("timestamp", ""))]

    def filter_by_access(self, entries: list[dict[str, Any]], user_role: str) -> list[dict[str, Any]]:
        return [e for e in entries if self.get_policy(e.get("policy", "default")).can_access(user_role)]