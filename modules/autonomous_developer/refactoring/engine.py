"""Refactoring engine — deterministic, safe source transformations.

Applies reversible transformations (identifier renames, text replacement) to
files under the generator config (size caps, backups, atomic writes) and the
security rules (path allowlist, project-root escape guard), mirroring the code
generator's write safety. Supports dry runs for planning-only flows.
"""
from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.security_rules import SecurityRules
from modules.autonomous_developer.core.exceptions import GenerationError, SecurityError

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def rename_symbol(source: str, old: str, new: str) -> str:
    """Rename an identifier ``old`` → ``new`` with word boundaries.

    Occurrences inside longer identifiers (``foo_bar`` for ``foo``) are left
    untouched. Invalid identifiers make the call a no-op.
    """
    if not _IDENTIFIER.fullmatch(old) or not _IDENTIFIER.fullmatch(new):
        return source
    pattern = re.compile(rf"\b{re.escape(old)}\b")
    return pattern.sub(lambda _match: new, source)


@dataclass(slots=True)
class Transformation:
    """One deterministic transformation applied to a file's content."""

    kind: str  # "rename" | "replace"
    old: str
    new: str
    count: int = -1  # only meaningful for "replace"; < 0 == all occurrences

    def apply(self, source: str) -> str:
        if self.kind == "rename":
            return rename_symbol(source, self.old, self.new)
        if self.kind == "replace":
            if self.count >= 0:
                return source.replace(self.old, self.new, self.count)
            return source.replace(self.old, self.new)
        return source  # unknown kind: no-op


@dataclass(slots=True)
class RefactorChange:
    """A file plus the transformations to apply to it."""

    path: str
    transformations: list[Transformation] = field(default_factory=list)


@dataclass(slots=True)
class RefactorResult:
    """Outcome of applying refactoring changes to files."""

    changed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    backups: list[str] = field(default_factory=list)
    dry_run: bool = False

    @property
    def success(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "changed": list(self.changed),
            "unchanged": list(self.unchanged),
            "skipped": list(self.skipped),
            "errors": list(self.errors),
            "backups": list(self.backups),
            "dry_run": self.dry_run,
        }


class RefactoringEngine:
    """Applies RefactorChange objects under generator + security rules."""

    def __init__(
        self,
        config: GeneratorConfig | None = None,
        security: SecurityRules | None = None,
    ) -> None:
        self.config = config or GeneratorConfig()
        self.security = security or SecurityRules()

    def apply_refactor(
        self,
        changes: list[RefactorChange],
        *,
        project_root: str | Path,
        dry_run: bool = False,
    ) -> RefactorResult:
        """Apply ``changes`` under ``project_root`` and report the outcome."""
        root = Path(project_root).resolve()
        result = RefactorResult(dry_run=dry_run)
        for change in changes[: self.config.max_files_per_task]:
            try:
                self._apply_one(change, root, result)
            except (GenerationError, SecurityError) as exc:
                result.errors.append({"path": change.path, "error": str(exc)})
        return result

    def _apply_one(self, change: RefactorChange, root: Path, result: RefactorResult) -> None:
        path = (root / change.path).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            raise SecurityError(f"Path escapes project root: {change.path}")
        if not self.security.is_path_allowed(path, root):
            raise SecurityError(f"Path not allowed: {change.path}")
        if not path.exists():
            result.skipped.append(f"{change.path} (missing)")
            return

        source = path.read_text(encoding=self.config.encoding)
        updated = source
        for transformation in change.transformations:
            updated = transformation.apply(updated)

        if updated == source:
            result.unchanged.append(change.path)
            return
        if result.dry_run:
            result.changed.append(change.path)
            return
        if self.config.create_backups:
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            result.backups.append(str(backup))
        self._write(path, updated)
        result.changed.append(change.path)

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

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> RefactorResult:
        """Runtime component entry point for refactoring one file.

        Reads ``path`` (required) and ``transformations`` (required, list of
        dicts or Transformation objects) from kwargs.
        """
        path = kwargs.get("path")
        if not path:
            raise GenerationError("A target path is required for refactoring")
        raw = kwargs.get("transformations") or kwargs.get("transforms")
        if not raw:
            raise GenerationError("No transformations provided for refactoring")
        transformations = [
            t if isinstance(t, Transformation) else Transformation(**t) for t in raw
        ]
        result = self.apply_refactor(
            [RefactorChange(path=path, transformations=transformations)],
            project_root=ctx.config.project_root,
            dry_run=bool(kwargs.get("dry_run", False)),
        )
        ctx.record("refactored_files", len(result.changed))
        ctx.record("refactor_unchanged", len(result.unchanged))
        ctx.record("refactor_errors", len(result.errors))
        ctx.publish(
            "refactor.completed",
            {
                "changed": len(result.changed),
                "unchanged": len(result.unchanged),
                "errors": len(result.errors),
            },
        )
        return result
