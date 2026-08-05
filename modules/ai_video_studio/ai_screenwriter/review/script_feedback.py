"""Script feedback — aggregates review signals into actionable feedback."""
from __future__ import annotations

from typing import Any


class ScriptFeedback:
    """Builds human-readable feedback from review results."""

    def build(self, review: dict[str, Any]) -> list[str]:
        feedback = []
        if review.get("issues"):
            feedback.extend(f"Issue: {issue}" for issue in review["issues"])
        else:
            feedback.append("No blocking issues found.")
        score = review.get("score", 0.0)
        if score >= 0.9:
            feedback.append("Ready for production.")
        elif score >= 0.7:
            feedback.append("Minor polish recommended.")
        else:
            feedback.append("Substantial rewrite recommended.")
        return feedback


_script_feedback: ScriptFeedback | None = None


def get_script_feedback() -> ScriptFeedback:
    global _script_feedback
    if _script_feedback is None:
        _script_feedback = ScriptFeedback()
    return _script_feedback
