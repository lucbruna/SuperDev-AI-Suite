"""Code reviewer skill — structured code review checklist."""
from __future__ import annotations
from typing import Any


class CodeReviewerSkill:
    """Produce a code review plan with severity-ranked checkpoints."""

    skill_id = "code_reviewer"
    skill_name = "Code Reviewer"
    skill_version = "1.0.0"
    skill_description = "Structured code review checklist ranked by severity."
    skill_category = "development"
    skill_tags = ["development", "review", "quality", "code"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        change: str,
        *,
        language: str = "python",
        language_tag: str = "en",
    ) -> dict[str, Any]:
        """Return a review checklist with severity buckets."""
        return {
            "change": change,
            "language": language,
            "language_tag": language_tag,
            "checklist": [
                {"severity": "blocker", "item": "Correctness: does the change do what it claims?"},
                {"severity": "blocker", "item": "Security: any injection, secret, or auth issue?"},
                {"severity": "major", "item": "Edge cases: empty inputs, errors, concurrency?"},
                {"severity": "major", "item": "Performance: obvious hot paths or N+1 queries?"},
                {"severity": "minor", "item": "Naming and structure consistency."},
                {"severity": "minor", "item": "Tests: are the important paths covered?"},
                {"severity": "nit", "item": "Formatting and comments."},
            ],
            "process": "review diff → run tests → verify edge cases → approve or request changes",
        }
