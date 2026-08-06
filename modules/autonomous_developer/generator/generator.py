"""Code generator — executes planned file changes safely.

Applies :class:`FileChange` objects from a plan's tasks to disk under the
generator config (size caps, allowed operations, atomic writes, backups) and
the security rules (path allowlist, blocked patterns, project-root escape
guard). Supports dry runs for planning-only flows.
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from modules.autonomous_developer.config.constants import (
    OP_CREATE,
    OP_DELETE,
    OP_MODIFY,
    PHASE_PLAN,
)
from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.risk_policy import enforce_task_risks
from modules.autonomous_developer.config.security_rules import SecurityRules
from modules.autonomous_developer.core.exceptions import GenerationError, SecurityError
from modules.autonomous_developer.core.models import FileChange


@dataclass(slots=True)
class GenerationResult:
    """Outcome of applying a batch of file changes."""

    written: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    backups: list[str] = field(default_factory=list)
    dry_run: bool = False

    @property
    def success(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "written": list(self.written),
            "skipped": list(self.skipped),
            "errors": list(self.errors),
            "backups": list(self.backups),
            "dry_run": self.dry_run,
        }


class CodeGenerator:
    """Applies FileChange objects under generator + security rules."""

    def __init__(
        self,
        config: GeneratorConfig | None = None,
        security: SecurityRules | None = None,
    ) -> None:
        self.config = config or GeneratorConfig()
        self.security = security or SecurityRules()

    def apply_changes(
        self,
        changes: list[FileChange],
        *,
        project_root: str | Path,
        dry_run: bool = False,
    ) -> GenerationResult:
        """Apply ``changes`` under ``project_root`` and report the outcome."""
        root = Path(project_root).resolve()
        result = GenerationResult(dry_run=dry_run)
        if len(changes) > self.config.max_files_per_task:
            result.errors.append(
                {
                    "path": "*",
                    "error": (
                        f"Too many files ({len(changes)} > "
                        f"{self.config.max_files_per_task})"
                    ),
                }
            )
        for change in changes[: self.config.max_files_per_task]:
            try:
                self._apply_one(change, root, result)
            except (GenerationError, SecurityError) as exc:
                result.errors.append({"path": change.path, "error": str(exc)})
        return result

    def _apply_one(self, change: FileChange, root: Path, result: GenerationResult) -> None:
        path = (root / change.path).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            raise SecurityError(f"Path escapes project root: {change.path}")
        if not self.security.is_path_allowed(path, root):
            raise SecurityError(f"Path not allowed: {change.path}")
        if change.content is not None and change.content_size > self.config.max_file_size_bytes:
            raise GenerationError(
                f"File too large ({change.content_size} bytes, "
                f"max {self.config.max_file_size_bytes})"
            )

        exists = path.exists()
        op = change.operation
        if op == OP_CREATE:
            if not self.config.allow_new_files:
                result.skipped.append(f"{change.path} (new files disabled)")
                return
            if exists:
                result.skipped.append(f"{change.path} (already exists)")
                return
            if change.content is None:
                result.skipped.append(f"{change.path} (no content)")
                return
            if not result.dry_run:
                self._write(path, change.content)
            result.written.append(change.path)
        elif op == OP_MODIFY:
            if not self.config.allow_modify_existing:
                result.skipped.append(f"{change.path} (modify disabled)")
                return
            if not exists:
                result.skipped.append(f"{change.path} (missing)")
                return
            if change.content is None:
                result.skipped.append(f"{change.path} (no content)")
                return
            if not result.dry_run:
                if self.config.create_backups:
                    backup = path.with_suffix(path.suffix + ".bak")
                    shutil.copy2(path, backup)
                    result.backups.append(str(backup))
                self._write(path, change.content)
            result.written.append(change.path)
        elif op == OP_DELETE:
            if not self.config.allow_delete:
                result.skipped.append(f"{change.path} (deletes disabled)")
                return
            if not exists:
                result.skipped.append(f"{change.path} (missing)")
                return
            if not result.dry_run:
                path.unlink()
            result.written.append(change.path)
        else:
            result.skipped.append(f"{change.path} (unknown operation {op})")

    def _write(self, path: Path, content: str) -> None:
        """Atomic-ish write: temp file in the same directory, then replace."""
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.parent / f".{path.name}.tmp"
        try:
            tmp.write_text(content, encoding=self.config.encoding, newline=self.config.newline)
            os.replace(tmp, path)
        finally:
            if tmp.exists():
                tmp.unlink(missing_ok=True)

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> GenerationResult:
        """Runtime component entry point (registers in the default registry).

        Pulls the plan artifact from the context, collects every task's file
        changes and applies them under the configured project root.
        """
        plan = ctx.get_artifact(PHASE_PLAN)
        if plan is None:
            raise GenerationError("No plan artifact; run the planner phase first")
        violations = enforce_task_risks(plan.tasks, self.config.max_risk_level)
        if violations:
            raise SecurityError(
                "Plan blocked by risk policy: " + "; ".join(violations),
                context={
                    "violations": violations,
                    "max_risk_level": self.config.max_risk_level,
                },
            )
        changes = [file_change for task in plan.tasks for file_change in task.files]
        dry_run = bool(kwargs.get("dry_run", False))
        result = self.apply_changes(
            changes, project_root=ctx.config.project_root, dry_run=dry_run
        )
        ctx.record("files_written", len(result.written))
        ctx.record("files_skipped", len(result.skipped))
        ctx.record("files_errors", len(result.errors))
        ctx.publish(
            "implementation.completed",
            {
                "written": len(result.written),
                "skipped": len(result.skipped),
                "errors": len(result.errors),
            },
        )
        return result
