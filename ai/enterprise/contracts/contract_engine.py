"""Contract engine."""

from __future__ import annotations

import time
from typing import Any


class ContractEngine:
    def __init__(self) -> None:
        self._contracts: dict[str, dict[str, Any]] = {}
        self._started = False

    def start(self) -> None:
        self._started = True

    def create(
        self, org_id: str, title: str, terms: dict[str, Any] | None = None, start_date: float = 0, end_date: float = 0
    ) -> dict[str, Any]:
        import uuid

        cid = str(uuid.uuid4())[:8]
        contract = {
            "id": cid,
            "org_id": org_id,
            "title": title,
            "terms": terms or {},
            "status": "active",
            "start_date": start_date or time.time(),
            "end_date": end_date,
            "created_at": time.time(),
        }
        self._contracts[cid] = contract
        return contract

    def get(self, contract_id: str) -> dict[str, Any] | None:
        return self._contracts.get(contract_id)

    def update(self, contract_id: str, **kwargs: Any) -> dict[str, Any] | None:
        c = self._contracts.get(contract_id)
        if c:
            c.update(kwargs)
            return c
        return None

    def terminate(self, contract_id: str) -> bool:
        c = self._contracts.get(contract_id)
        if c:
            c["status"] = "terminated"
            c["terminated_at"] = time.time()
            return True
        return False

    def list_by_org(self, org_id: str) -> list[dict[str, Any]]:
        return [c for c in self._contracts.values() if c["org_id"] == org_id]

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._contracts.values())

    def count(self) -> int:
        return len(self._contracts)

    def is_running(self) -> bool:
        return self._started
