"""Contract customer."""
from __future__ import annotations
from typing import Any, Dict, List

class ContractCustomer:
    def __init__(self) -> None:
        self._customers: Dict[str, Dict[str, Any]] = {}
    def set(self, contract_id: str, org_name: str, contact_email: str, contact_name: str = "", phone: str = "") -> Dict[str, Any]:
        customer = {"contract_id": contract_id, "org_name": org_name, "contact_email": contact_email, "contact_name": contact_name, "phone": phone}
        self._customers[contract_id] = customer
        return customer
    def get(self, contract_id: str) -> Dict[str, Any]:
        return self._customers.get(contract_id, {})
    def update(self, contract_id: str, **kwargs: Any) -> Dict[str, Any]:
        if contract_id in self._customers:
            self._customers[contract_id].update(kwargs)
            return self._customers[contract_id]
        return {}
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._customers)
    def find_by_email(self, email: str) -> List[Dict[str, Any]]:
        return [c for c in self._customers.values() if c.get("contact_email") == email]
    def delete(self, contract_id: str) -> bool:
        if contract_id in self._customers:
            del self._customers[contract_id]
            return True
        return False
