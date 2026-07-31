"""Contract compliance."""
from __future__ import annotations
from typing import Any, Dict, List

class ComplianceManager:
    def __init__(self) -> None:
        self._compliance: Dict[str, Dict[str, Any]] = {}
    def set_compliance(self, contract_id: str, framework: str, status: str = "compliant") -> Dict[str, Any]:
        entry = {"framework": framework, "status": status, "checks": []}
        self._compliance[contract_id] = entry
        return entry
    def get_compliance(self, contract_id: str) -> Dict[str, Any]:
        return self._compliance.get(contract_id, {})
    def add_check(self, contract_id: str, check_name: str, passed: bool) -> Dict[str, Any]:
        compliance = self._compliance.get(contract_id)
        if compliance:
            check = {"name": check_name, "passed": passed}
            compliance["checks"].append(check)
            all_passed = all(c["passed"] for c in compliance["checks"])
            compliance["status"] = "compliant" if all_passed else "non_compliant"
            return check
        return {}
    def is_compliant(self, contract_id: str) -> bool:
        return self._compliance.get(contract_id, {}).get("status") == "compliant"
    def get_checks(self, contract_id: str) -> List[Dict[str, Any]]:
        return self._compliance.get(contract_id, {}).get("checks", [])
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._compliance)
    def delete(self, contract_id: str) -> bool:
        if contract_id in self._compliance:
            del self._compliance[contract_id]
            return True
        return False
