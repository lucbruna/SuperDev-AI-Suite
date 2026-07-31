"""Company profile."""
from __future__ import annotations

from typing import Any


class CompanyProfile:
    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, Any]] = {}
    def create(self, org_id: str, legal_name: str, trade_name: str = "", cnpj: str = "", address: dict[str, str] | None = None) -> dict[str, Any]:
        profile = {"org_id": org_id, "legal_name": legal_name, "trade_name": trade_name or legal_name, "cnpj": cnpj, "address": address or {}, "phone": "", "email": "", "website": ""}
        self._profiles[org_id] = profile
        return profile
    def get(self, org_id: str) -> dict[str, Any]:
        return self._profiles.get(org_id, {})
    def update(self, org_id: str, **kwargs: Any) -> dict[str, Any]:
        if org_id in self._profiles:
            self._profiles[org_id].update(kwargs)
            return self._profiles[org_id]
        return {}
    def delete(self, org_id: str) -> bool:
        if org_id in self._profiles:
            del self._profiles[org_id]
            return True
        return False
    def list_all(self) -> dict[str, dict[str, Any]]:
        return dict(self._profiles)
