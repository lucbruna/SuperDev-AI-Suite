"""Unit tests for the Autonomous Developer refactoring engine (Phase D)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import GenerationError
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.refactoring.engine import (
    RefactorChange,
    RefactoringEngine,
    Transformation,
    rename_symbol,
)


class TestRenameSymbol:
    def test_renames_identifier(self) -> None:
        assert rename_symbol("foo = 1\nprint(foo)", "foo", "bar") == "bar = 1\nprint(bar)"

    def test_leaves_longer_identifiers_alone(self) -> None:
        assert rename_symbol("foo_bar = 1\nfoo = 2", "foo", "bar") == "foo_bar = 1\nbar = 2"

    def test_invalid_old_identifier_is_noop(self) -> None:
        assert rename_symbol("foo = 1", "foo bar", "bar") == "foo = 1"

    def test_invalid_new_identifier_is_noop(self) -> None:
        assert rename_symbol("foo = 1", "foo", "1bar") == "foo = 1"

    def test_backslash_replacement_is_noop(self) -> None:
        # Backslashes are not valid identifier characters, so the rename is a
        # no-op (and no re.sub replacement escaping can occur).
        assert rename_symbol("foo = 1", "foo", "x\\y") == "foo = 1"

    def test_missing_old_is_noop(self) -> None:
        assert rename_symbol("foo = 1", "missing", "bar") == "foo = 1"


class TestTransformation:
    def test_rename_kind(self) -> None:
        assert Transformation("rename", "foo", "bar").apply("foo foo") == "bar bar"

    def test_replace_all(self) -> None:
        assert Transformation("replace", "foo", "bar").apply("foo foo foo") == "bar bar bar"

    def test_replace_limited_count(self) -> None:
        assert Transformation("replace", "foo", "bar", count=1).apply("foo foo foo") == "bar foo foo"

    def test_unknown_kind_is_noop(self) -> None:
        assert Transformation("explode", "foo", "bar").apply("foo foo") == "foo foo"


class TestApplyRefactor:
    def test_rename_applies_and_backs_up(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("foo = 1\nprint(foo)", encoding="utf-8")
        result = RefactoringEngine().apply_refactor(
            [RefactorChange(path="app.py", transformations=[Transformation("rename", "foo", "bar")])],
            project_root=tmp_path,
        )
        assert result.success
        assert result.changed == ["app.py"]
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "bar = 1\nprint(bar)"
        assert (tmp_path / "app.py.bak").read_text(encoding="utf-8") == "foo = 1\nprint(foo)"
        assert result.backups == [str(tmp_path / "app.py.bak")]

    def test_transformations_apply_in_order(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("a = 1\nb = 2", encoding="utf-8")
        engine = RefactoringEngine()
        engine.apply_refactor(
            [
                RefactorChange(
                    path="app.py",
                    transformations=[
                        Transformation("replace", "a", "x"),
                        Transformation("replace", "b", "y"),
                    ],
                )
            ],
            project_root=tmp_path,
        )
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "x = 1\ny = 2"

    def test_no_change_reported_unchanged(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("a = 1", encoding="utf-8")
        result = RefactoringEngine().apply_refactor(
            [RefactorChange(path="app.py", transformations=[Transformation("replace", "zzz", "y")])],
            project_root=tmp_path,
        )
        assert result.changed == []
        assert result.unchanged == ["app.py"]
        assert not (tmp_path / "app.py.bak").exists()

    def test_missing_file_skipped(self, tmp_path) -> None:
        result = RefactoringEngine().apply_refactor(
            [RefactorChange(path="app.py", transformations=[Transformation("replace", "a", "b")])],
            project_root=tmp_path,
        )
        assert result.skipped == ["app.py (missing)"]

    def test_dry_run_marks_changed_without_writing(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("foo = 1", encoding="utf-8")
        result = RefactoringEngine().apply_refactor(
            [RefactorChange(path="app.py", transformations=[Transformation("rename", "foo", "bar")])],
            project_root=tmp_path,
            dry_run=True,
        )
        assert result.dry_run
        assert result.changed == ["app.py"]
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "foo = 1"

    def test_path_escape_rejected(self, tmp_path) -> None:
        result = RefactoringEngine().apply_refactor(
            [RefactorChange(path="../escape.txt", transformations=[])],
            project_root=tmp_path,
        )
        assert not result.success
        assert "Path escapes project root" in result.errors[0]["error"]

    def test_blocked_pattern_rejected(self, tmp_path) -> None:
        (tmp_path / ".env").write_text("SECRET=x", encoding="utf-8")
        result = RefactoringEngine().apply_refactor(
            [RefactorChange(path=".env", transformations=[Transformation("replace", "SECRET", "X")])],
            project_root=tmp_path,
        )
        assert not result.success
        assert result.errors[0]["error"] == "Path not allowed: .env"


class TestRefactoringRun:
    def _context(self, tmp_path) -> DeveloperContext:
        config = DeveloperConfig(project_root=str(tmp_path))
        return DeveloperContext(config=config, registry=DeveloperRegistry())

    def test_run_without_path_raises(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        with pytest.raises(GenerationError, match="A target path is required"):
            RefactoringEngine().run(ctx, "goal")

    def test_run_without_transformations_raises(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        with pytest.raises(GenerationError, match="No transformations provided"):
            RefactoringEngine().run(ctx, "goal", path="app.py")

    def test_run_applies_dict_transformations(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        (tmp_path / "app.py").write_text("foo = 1", encoding="utf-8")
        result = RefactoringEngine().run(
            ctx,
            "goal",
            path="app.py",
            transformations=[{"kind": "rename", "old": "foo", "new": "bar"}],
        )
        assert result.changed == ["app.py"]
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "bar = 1"
        assert ctx.stats["refactored_files"] == 1
        events = [e.type for e in ctx.bus.history(event_type="refactor.completed")]
        assert events == ["refactor.completed"]

    def test_run_accepts_transformation_objects(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        (tmp_path / "app.py").write_text("foo = 1", encoding="utf-8")
        result = RefactoringEngine().run(
            ctx, "goal", path="app.py", transformations=[Transformation("rename", "foo", "bar")]
        )
        assert result.changed == ["app.py"]
