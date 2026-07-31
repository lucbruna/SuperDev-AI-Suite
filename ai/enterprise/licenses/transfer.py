"""License transfer."""

from __future__ import annotations

import time
from typing import Any


class LicenseTransfer:
    def __init__(self, allow_transfer: bool = True) -> None:
        self._allow_transfer = allow_transfer
        self._transfers: list[dict[str, Any]] = []

    def transfer(self, license_id: str, from_org: str, to_org: str) -> dict[str, Any]:
        if not self._allow_transfer:
            return {"error": "transfer_not_allowed"}
        entry = {"license_id": license_id, "from_org": from_org, "to_org": to_org, "transferred_at": time.time()}
        self._transfers.append(entry)
        return entry

    def list_transfers(self) -> list[dict[str, Any]]:
        return list(self._transfers)

    def get_by_license(self, license_id: str) -> list[dict[str, Any]]:
        return [t for t in self._transfers if t["license_id"] == license_id]

    def count(self) -> int:
        return len(self._transfers)

    def is_allowed(self) -> bool:
        return self._allow_transfer

    def set_allow_transfer(self, allowed: bool) -> None:
        self._allow_transfer = allowed
