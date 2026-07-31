"""Auto-fix capability."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class AutoFix:
    def __init__(self) -> None:
        self._fixes: dict[str, Callable[[], bool]] = {}
        self._history: list[dict[str, Any]] = []

    def register_fix(self, issue_type: str, fix_func: Callable[[], bool]) -> None:
        self._fixes[issue_type] = fix_func

    def attempt_fix(self, issue_type: str) -> dict[str, Any]:
        fix = self._fixes.get(issue_type)
        if not fix:
            return {"issue": issue_type, "status": "no_fix_available"}
        try:
            success = fix()
            result = {"issue": issue_type, "status": "fixed" if success else "fix_failed"}
        except Exception as e:
            result = {"issue": issue_type, "status": "error", "error": str(e)}
        self._history.append(result)
        return result

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]

    def list_fixes(self) -> list[str]:
        return list(self._fixes.keys())

    def remove_fix(self, issue_type: str) -> bool:
        if issue_type in self._fixes:
            del self._fixes[issue_type]
            return True
        return False
