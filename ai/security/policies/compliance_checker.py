"""Policy compliance checker."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class ComplianceCheck:
    def __init__(self, check_id: str, name: str, description: str, standard: str) -> None:
        self.check_id = check_id
        self.name = name
        self.description = description
        self.standard = standard
        self.status = "not_checked"
        self.last_checked: Optional[float] = None

class PolicyComplianceChecker:
    def __init__(self) -> None:
        self._checks: Dict[str, ComplianceCheck] = {}
        self._results: List[Dict[str, Any]] = []
    def add_check(self, name: str, description: str, standard: str) -> ComplianceCheck:
        check_id = str(uuid.uuid4())[:8]
        check = ComplianceCheck(check_id, name, description, standard)
        self._checks[check_id] = check
        return check
    def run_check(self, check_id: str, passed: bool, details: str = "") -> Dict[str, Any]:
        check = self._checks.get(check_id)
        if not check:
            return {"error": "check_not_found"}
        check.status = "pass" if passed else "fail"
        check.last_checked = time.time()
        result = {"check_id": check_id, "name": check.name, "status": check.status, "details": details, "timestamp": time.time()}
        self._results.append(result)
        return result
    def get_compliance_status(self, standard: str = "") -> Dict[str, Any]:
        checks = list(self._checks.values())
        if standard:
            checks = [c for c in checks if c.standard == standard]
        total = len(checks)
        passed = sum(1 for c in checks if c.status == "pass")
        failed = sum(1 for c in checks if c.status == "fail")
        not_checked = sum(1 for c in checks if c.status == "not_checked")
        return {"total": total, "passed": passed, "failed": failed, "not_checked": not_checked, "score": (passed / max(total, 1)) * 100}
    def get_results(self, check_id: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        results = self._results
        if check_id:
            results = [r for r in results if r["check_id"] == check_id]
        return results[-limit:]
    def list_checks(self, standard: str = "") -> List[str]:
        if standard:
            return [c.check_id for c in self._checks.values() if c.standard == standard]
        return list(self._checks.keys())
