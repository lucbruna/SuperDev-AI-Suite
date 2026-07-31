"""Contract renewal."""

from __future__ import annotations

import time
from typing import Any


class ContractRenewal:
    def __init__(self) -> None:
        self._renewals: dict[str, dict[str, Any]] = {}

    def schedule(self, contract_id: str, renewal_date: float, new_end_date: float) -> dict[str, Any]:
        renewal = {
            "contract_id": contract_id,
            "renewal_date": renewal_date,
            "new_end_date": new_end_date,
            "status": "scheduled",
        }
        self._renewals[contract_id] = renewal
        return renewal

    def renew(self, contract_id: str) -> dict[str, Any]:
        renewal = self._renewals.get(contract_id)
        if renewal:
            renewal["status"] = "completed"
            renewal["renewed_at"] = time.time()
            return renewal
        return {"error": "not_found"}

    def cancel(self, contract_id: str) -> bool:
        if contract_id in self._renewals:
            self._renewals[contract_id]["status"] = "cancelled"
            return True
        return False

    def get(self, contract_id: str) -> dict[str, Any]:
        return self._renewals.get(contract_id, {})

    def get_pending(self) -> list[dict[str, Any]]:
        return [r for r in self._renewals.values() if r["status"] == "scheduled"]

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._renewals.values())

    def count(self) -> int:
        return len(self._renewals)
