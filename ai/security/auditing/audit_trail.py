"""Audit trail management."""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any


class AuditTrail:
    def __init__(self) -> None:
        self._trails: dict[str, list[dict[str, Any]]] = {}
        self._hash_chain: list[str] = []

    def start_trail(self, trail_id: str) -> str:
        if trail_id not in self._trails:
            self._trails[trail_id] = []
        return trail_id

    def add_event(self, trail_id: str, event_type: str, user_id: str, data: str = "") -> dict[str, Any]:
        entry = {
            "event_id": str(uuid.uuid4())[:8],
            "type": event_type,
            "user": user_id,
            "data": data,
            "timestamp": time.time(),
        }
        self._trails.setdefault(trail_id, []).append(entry)
        prev_hash = self._hash_chain[-1] if self._hash_chain else "genesis"
        entry_hash = hashlib.sha256((prev_hash + str(entry)).encode()).hexdigest()[:16]
        self._hash_chain.append(entry_hash)
        entry["hash"] = entry_hash
        return entry

    def get_trail(self, trail_id: str) -> list[dict[str, Any]]:
        return list(self._trails.get(trail_id, []))

    def verify_integrity(self, trail_id: str) -> bool:
        trail = self._trails.get(trail_id, [])
        return len(trail) > 0

    def get_all_trails(self) -> list[str]:
        return list(self._trails.keys())

    def delete_trail(self, trail_id: str) -> bool:
        if trail_id in self._trails:
            del self._trails[trail_id]
            return True
        return False

    def count_events(self, trail_id: str) -> int:
        return len(self._trails.get(trail_id, []))
