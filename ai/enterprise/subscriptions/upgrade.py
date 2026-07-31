"""Subscription upgrade."""

from __future__ import annotations

import time
from typing import Any


class UpgradeManager:
    def __init__(self) -> None:
        self._upgrades: list[dict[str, Any]] = []

    def upgrade(self, subscription_id: str, from_plan: str, to_plan: str, prorated: float = 0.0) -> dict[str, Any]:
        entry = {
            "subscription_id": subscription_id,
            "from_plan": from_plan,
            "to_plan": to_plan,
            "prorated": prorated,
            "upgraded_at": time.time(),
        }
        self._upgrades.append(entry)
        return entry

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._upgrades)

    def get_by_subscription(self, subscription_id: str) -> list[dict[str, Any]]:
        return [u for u in self._upgrades if u["subscription_id"] == subscription_id]

    def count(self) -> int:
        return len(self._upgrades)

    def get_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._upgrades[-limit:]
