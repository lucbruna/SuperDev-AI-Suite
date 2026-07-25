from __future__ import annotations as __

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


DATA_RETENTION_POLICIES: Dict[str, int] = {
    "audit_logs": 365,
    "analytics_events": 90,
    "user_sessions": 30,
    "api_requests": 180,
    "error_logs": 90,
    "billing_records": 2555,
    "user_data": 730,
    "temporary_files": 7,
    "backups": 30,
    "email_logs": 365,
}


class DataRetentionPolicy:
    def __init__(self) -> None:
        self._policies = dict(DATA_RETENTION_POLICIES)
        self._data_store: Dict[str, List[Dict[str, Any]]] = {}

    def get_policy(self, data_type: str) -> int:
        return self._policies.get(data_type, 30)

    def set_policy(self, data_type: str, retention_days: int) -> None:
        if retention_days < 1:
            raise ValueError("Retention days must be at least 1")
        self._policies[data_type] = retention_days

    async def apply_retention(self) -> Dict[str, int]:
        await asyncio.sleep(0.03)
        now = datetime.utcnow()
        purged: Dict[str, int] = {}

        for data_type, days in self._policies.items():
            cutoff = now - timedelta(days=days)
            records = self._data_store.get(data_type, [])
            before = len(records)
            self._data_store[data_type] = [
                r
                for r in records
                if r.get("created_at")
                and isinstance(r["created_at"], datetime)
                and r["created_at"] > cutoff
            ]
            purged[data_type] = before - len(self._data_store[data_type])

        return purged

    async def get_retention_report(self) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        now = datetime.utcnow()
        type_counts: Dict[str, Dict[str, Any]] = {}

        for data_type, days in self._policies.items():
            cutoff = now - timedelta(days=days)
            records = self._data_store.get(data_type, [])
            total = len(records)

            expired = sum(
                1
                for r in records
                if r.get("created_at")
                and isinstance(r["created_at"], datetime)
                and r["created_at"] <= cutoff
            )

            age_groups = {"<7d": 0, "7-30d": 0, "30-90d": 0, ">90d": 0}
            for r in records:
                age = (now - r["created_at"]).days if isinstance(r.get("created_at"), datetime) else 0
                if age < 7:
                    age_groups["<7d"] += 1
                elif age < 30:
                    age_groups["7-30d"] += 1
                elif age < 90:
                    age_groups["30-90d"] += 1
                else:
                    age_groups[">90d"] += 1

            type_counts[data_type] = {
                "retention_days": days,
                "total_records": total,
                "expired_records": expired,
                "age_distribution": age_groups,
            }

        return {
            "generated_at": now.isoformat(),
            "policies": type_counts,
            "total_policies": len(self._policies),
        }

    async def store_record(
        self, data_type: str, record: Dict[str, Any]
    ) -> None:
        await asyncio.sleep(0.01)
        if data_type not in self._data_store:
            self._data_store[data_type] = []
        record.setdefault("created_at", datetime.utcnow())
        record["data_type"] = data_type
        self._data_store[data_type].append(record)
