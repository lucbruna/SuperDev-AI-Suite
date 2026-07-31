"""Company profile."""
from __future__ import annotations
from typing import Any, Dict, Optional

class CompanyProfile:
    def __init__(self) -> None:
        self._profiles: Dict[str, Dict[str, Any]] = {}
    def create(self, org_id: str, legal_name: str, trade_name: str = "", cnpj: str = "", address: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        profile = {"org_id": org_id, "legal_name": legal_name, "trade_name": trade_name or legal_name, "cnpj": cnpj, "address": address or {}, "phone": "", "email": "", "website": ""}
        self._profiles[org_id] = profile
        return profile
    def get(self, org_id: str) -> Dict[str, Any]:
        return self._profiles.get(org_id, {})
    def update(self, org_id: str, **kwargs: Any) -> Dict[str, Any]:
        if org_id in self._profiles:
            self._profiles[org_id].update(kwargs)
            return self._profiles[org_id]
        return {}
    def delete(self, org_id: str) -> bool:
        if org_id in self._profiles:
            del self._profiles[org_id]
            return True
        return False
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._profiles)
