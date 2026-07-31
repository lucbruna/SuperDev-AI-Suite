"""License manager."""

from __future__ import annotations


class LicenseManager:
    def __init__(self) -> None:
        self._assignments: dict[str, str] = {}

    def assign(self, license_id: str, org_id: str) -> bool:
        self._assignments[license_id] = org_id
        return True

    def unassign(self, license_id: str) -> bool:
        if license_id in self._assignments:
            del self._assignments[license_id]
            return True
        return False

    def get_org(self, license_id: str) -> str:
        return self._assignments.get(license_id, "")

    def list_by_org(self, org_id: str) -> list[str]:
        return [lid for lid, oid in self._assignments.items() if oid == org_id]

    def count(self) -> int:
        return len(self._assignments)

    def has_license(self, org_id: str) -> bool:
        return org_id in self._assignments.values()

    def list_all(self) -> dict[str, str]:
        return dict(self._assignments)
