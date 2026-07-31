"""Policy compliance checker."""

from __future__ import annotations

import time
import uuid
from typing import Any


class ComplianceCheck:
    def __init__(self, check_id: str, name: str, description: str, standard: str) -> None:
        self.check_id = check_id
        self.name = name
        self.description = description
        self.standard = standard
        self.status = "not_checked"
        self.last_checked: float | None = None


class PolicyComplianceChecker:
    def __init__(self) -> None:
        self._checks: dict[str, ComplianceCheck] = {}
        self._results: list[dict[str, Any]] = []

    def add_check(self, name: str, description: str, standard: str) -> ComplianceCheck:
        check_id = str(uuid.uuid4())[:8]
        check = ComplianceCheck(check_id, name, description, standard)
        self._checks[check_id] = check
        return check

    def run_check(self, check_id: str, passed: bool, details: str = "") -> dict[str, Any]:
        check = self._checks.get(check_id)
        if not check:
            return {"error": "check_not_found"}
        check.status = "pass" if passed else "fail"
        check.last_checked = time.time()
        result = {
            "check_id": check_id,
            "name": check.name,
            "status": check.status,
            "details": details,
            "timestamp": time.time(),
        }
        self._results.append(result)
        return result

    def get_compliance_status(self, standard: str = "") -> dict[str, Any]:
        checks = list(self._checks.values())
        if standard:
            checks = [c for c in checks if c.standard == standard]
        total = len(checks)
        passed = sum(1 for c in checks if c.status == "pass")
        failed = sum(1 for c in checks if c.status == "fail")
        not_checked = sum(1 for c in checks if c.status == "not_checked")
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "not_checked": not_checked,
            "score": (passed / max(total, 1)) * 100,
        }

    def get_results(self, check_id: str = "", limit: int = 100) -> list[dict[str, Any]]:
        results = self._results
        if check_id:
            results = [r for r in results if r["check_id"] == check_id]
        return results[-limit:]

    def list_checks(self, standard: str = "") -> list[str]:
        if standard:
            return [c.check_id for c in self._checks.values() if c.standard == standard]
        return list(self._checks.keys())
