"""Script reviewer — evaluates a generated script and returns score + issues."""
from __future__ import annotations

from typing import Any


class ScriptReviewer:
    """Reviews scripts against quality heuristics."""

    def review(self, script: dict[str, Any]) -> dict[str, Any]:
        text = script.get("text", "")
        words = len(text.split())
        issues: list[str] = []
        if words < 20:
            issues.append("Script too short — expand the body.")
        if words > 3000:
            issues.append("Script too long — consider splitting episodes.")
        if not text:
            issues.append("Script is empty.")
        sections = script.get("sections", [])
        if "intro" not in sections or "outro" not in sections:
            issues.append("Missing intro or outro section.")
        score = max(0.0, min(1.0, 1.0 - 0.1 * len(issues)))
        return {"score": round(score, 3), "issues": issues, "words": words}


_reviewer: ScriptReviewer | None = None


def get_script_reviewer() -> ScriptReviewer:
    global _reviewer
    if _reviewer is None:
        _reviewer = ScriptReviewer()
    return _reviewer
