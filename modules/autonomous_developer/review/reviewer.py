"""Code reviewer — deterministic change review against safety rules.

Reviews a batch of :class:`FileChange` objects against concrete, testable
checks: path escape / blocked patterns, secret-like content, file size and
missing content. Produces a :class:`ReviewVerdict` (approved,
changes_requested or rejected) with human-readable issues.
"""
from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

from modules.autonomous_developer.config.constants import OP_CREATE
from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.security_rules import SecurityRules, contains_secret
from modules.autonomous_developer.core.exceptions import GenerationError
from modules.autonomous_developer.core.models import FileChange, ReviewVerdict

VERDICT_APPROVED = "approved"
VERDICT_CHANGES_REQUESTED = "changes_requested"
VERDICT_REJECTED = "rejected"


def _change_from_spec(spec: FileChange | dict[str, Any]) -> FileChange:
    if isinstance(spec, FileChange):
        return spec
    return FileChange(
        path=spec.get("path", ""),
        content=spec.get("content"),
        operation=spec.get("operation", OP_CREATE),
        old_content=spec.get("old_content"),
        reason=spec.get("reason", ""),
    )


class CodeReviewer:
    """Reviews file changes and returns a ReviewVerdict."""

    def __init__(
        self,
        config: GeneratorConfig | None = None,
        security: SecurityRules | None = None,
    ) -> None:
        self.config = config or GeneratorConfig()
        self.security = security or SecurityRules()

    def review_changes(
        self,
        changes: list[FileChange | dict[str, Any]],
        *,
        task_id: str = "",
        project_root: str | Path | None = None,
    ) -> ReviewVerdict:
        """Review ``changes`` and return a structured verdict."""
        if not changes:
            return ReviewVerdict(
                task_id=task_id,
                verdict=VERDICT_CHANGES_REQUESTED,
                comments="No changes were provided for review.",
                issues=["No changes to review"],
            )
        root = Path(project_root).resolve() if project_root is not None else None
        issues: list[str] = []
        critical: list[str] = []
        for raw in changes:
            change = _change_from_spec(raw)
            if root is not None:
                path = (root / change.path).resolve()
                try:
                    path.relative_to(root)
                except ValueError:
                    critical.append(f"Path escapes project root: {change.path}")
                    continue
                if not self.security.is_path_allowed(path, root):
                    critical.append(f"Path not allowed: {change.path}")
                    continue
            elif self._blocked(change.path):
                critical.append(f"Path not allowed: {change.path}")
                continue
            if change.content is not None and contains_secret(change.content):
                critical.append(f"Secret-like content detected in {change.path}")
            if change.content is not None and change.content_size > self.config.max_file_size_bytes:
                issues.append(f"File too large: {change.path}")
            if change.operation == OP_CREATE and change.content is None:
                issues.append(f"Create without content: {change.path}")

        if critical:
            verdict = VERDICT_REJECTED
            comments = "Rejected: " + "; ".join(critical)
        elif issues:
            verdict = VERDICT_CHANGES_REQUESTED
            comments = "Changes requested: " + "; ".join(issues)
        else:
            verdict = VERDICT_APPROVED
            comments = "All checks passed."
        return ReviewVerdict(
            task_id=task_id,
            verdict=verdict,
            comments=comments,
            issues=critical + issues,
        )

    def _blocked(self, path: str) -> bool:
        p = Path(path)
        for pattern in self.security.blocked_patterns:
            if fnmatch.fnmatch(p.name, pattern) or fnmatch.fnmatch(str(p), pattern):
                return True
        return False

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> ReviewVerdict:
        """Runtime component entry point.

        Reviews ``changes`` from kwargs (list of FileChange/dicts) or, when
        absent, the file changes collected from the plan artifact.
        """
        raw = kwargs.get("changes")
        if raw is None:
            plan = ctx.get_artifact("plan")
            raw = (
                [file_change for task in plan.tasks for file_change in task.files]
                if plan is not None
                else []
            )
        verdict = self.review_changes(
            raw,
            task_id=str(kwargs.get("task_id", "")),
            project_root=ctx.config.project_root,
        )
        ctx.record("review_verdict", verdict.verdict)
        ctx.record("review_issues", len(verdict.issues))
        ctx.publish(
            "review.completed",
            {"task_id": verdict.task_id, "verdict": verdict.verdict, "issues": len(verdict.issues)},
        )
        if verdict.verdict == VERDICT_REJECTED:
            raise GenerationError(verdict.comments)
        return verdict
