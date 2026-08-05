"""Debugger skill — structured debugging playbook."""
from __future__ import annotations
from typing import Any


class DebuggerSkill:
    """Guide a systematic debugging session for a reported issue."""

    skill_id = "debugger"
    skill_name = "Debugger"
    skill_version = "1.0.0"
    skill_description = "Systematic debugging playbook: reproduce, isolate, fix, verify."
    skill_category = "development"
    skill_tags = ["development", "debugging", "troubleshooting", "bug"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        symptom: str,
        *,
        context: str = "unknown environment",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a debugging plan for the symptom."""
        return {
            "symptom": symptom,
            "context": context,
            "language": language,
            "playbook": [
                {"step": "Reproduce", "instruction": f"Find the minimal input that triggers '{symptom}'."},
                {"step": "Isolate", "instruction": "Bisect the change or component responsible."},
                {"step": "Hypothesize", "instruction": "Write one testable hypothesis at a time."},
                {"step": "Fix", "instruction": "Apply the smallest change that addresses the cause."},
                {"step": "Verify", "instruction": "Confirm the fix and run the regression suite."},
            ],
            "tips": ["read the error fully", "check recent changes", "add targeted logging"],
        }
