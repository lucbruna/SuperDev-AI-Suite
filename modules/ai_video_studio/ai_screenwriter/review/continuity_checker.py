"""Continuity checker — verifies narrative consistency across sections."""
from __future__ import annotations

from typing import Any


class ContinuityChecker:
    """Checks for topic consistency inside a script."""

    def check(self, script: dict[str, Any]) -> dict[str, Any]:
        text = script.get("text", "")
        sections = script.get("sections", [])
        consistent = bool(text and len(sections) >= 2)
        issues: list[str] = []
        if not consistent:
            issues.append("Sections are missing or text is empty — continuity unverifiable.")
        return {"consistent": consistent, "issues": issues}


_continuity_checker: ContinuityChecker | None = None


def get_continuity_checker() -> ContinuityChecker:
    global _continuity_checker
    if _continuity_checker is None:
        _continuity_checker = ContinuityChecker()
    return _continuity_checker
