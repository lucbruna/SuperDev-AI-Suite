"""Contract agreement."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class AgreementManager:
    def __init__(self) -> None:
        self._agreements: Dict[str, Dict[str, Any]] = {}
    def create(self, contract_id: str, parties: List[str], signed_by: str = "") -> Dict[str, Any]:
        agreement = {"contract_id": contract_id, "parties": parties, "signed_by": signed_by, "signed_at": time.time(), "status": "active"}
        self._agreements[contract_id] = agreement
        return agreement
    def get(self, contract_id: str) -> Dict[str, Any]:
        return self._agreements.get(contract_id, {})
    def sign(self, contract_id: str, signer: str) -> bool:
        agreement = self._agreements.get(contract_id)
        if agreement:
            agreement["signed_by"] = signer
            agreement["signed_at"] = time.time()
            return True
        return False
    def void(self, contract_id: str) -> bool:
        if contract_id in self._agreements:
            self._agreements[contract_id]["status"] = "void"
            return True
        return False
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._agreements.values())
    def list_active(self) -> List[Dict[str, Any]]:
        return [a for a in self._agreements.values() if a["status"] == "active"]
    def count(self) -> int:
        return len(self._agreements)
