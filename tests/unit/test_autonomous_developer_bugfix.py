"""Unit tests for the Autonomous Developer bug fixer (Phase D)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.bugfix.fixer import BugFixer
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import GenerationError
from modules.autonomous_developer.core.registry import DeveloperRegistry

TRACEBACK_IMPORT = """Traceback (most recent call last):
  File "app.py", line 12, in <module>
    import pandas
ModuleNotFoundError: No module named 'pandas'
"""

TRACEBACK_SYNTAX = """  File "app.py", line 3
    x =
       ^
SyntaxError: invalid syntax
"""


class TestAnalyze:
    def test_import_error_category_and_location(self) -> None:
        analysis = BugFixer().analyze(TRACEBACK_IMPORT)
        assert analysis.category == "import"
        assert analysis.error_type == "ModuleNotFoundError"
        assert analysis.message == "No module named 'pandas'"
        assert analysis.file == "app.py"
        assert analysis.line == 12
        assert analysis.summary == "ModuleNotFoundError: No module named 'pandas'"
        assert "Add the missing import for 'pandas'" in analysis.suggestions

    def test_syntax_error_category(self) -> None:
        analysis = BugFixer().analyze(TRACEBACK_SYNTAX)
        assert analysis.category == "syntax"
        assert analysis.error_type == "SyntaxError"
        assert analysis.file == "app.py"
        assert analysis.line == 3

    def test_name_error_category(self) -> None:
        analysis = BugFixer().analyze("NameError: name 'foo' is not defined")
        assert analysis.category == "name"
        assert "add the missing definition" in analysis.suggestions[0]

    def test_attribute_error_category(self) -> None:
        analysis = BugFixer().analyze(
            "AttributeError: 'NoneType' object has no attribute 'name'"
        )
        assert analysis.category == "attribute"

    def test_type_error_category(self) -> None:
        analysis = BugFixer().analyze(
            "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
        )
        assert analysis.category == "type"

    def test_value_error_category(self) -> None:
        analysis = BugFixer().analyze(
            "ValueError: invalid literal for int() with base 10: 'abc'"
        )
        assert analysis.category == "value"

    def test_key_error_category(self) -> None:
        analysis = BugFixer().analyze("KeyError: 'missing'")
        assert analysis.category == "lookup"

    def test_index_error_category(self) -> None:
        analysis = BugFixer().analyze("IndexError: list index out of range")
        assert analysis.category == "lookup"

    def test_unknown_error_falls_back_to_generic(self) -> None:
        analysis = BugFixer().analyze("Something bad happened")
        assert analysis.category == "generic"
        assert analysis.error_type == "Exception"
        assert analysis.summary == "Exception: Something bad happened"

    def test_empty_text(self) -> None:
        analysis = BugFixer().analyze("")
        assert analysis.category == "generic"

    def test_last_header_wins_in_traceback(self) -> None:
        text = (
            "  File \"a.py\", line 1\n    boom\nValueError: first\n"
            "ValueError: final failure"
        )
        analysis = BugFixer().analyze(text)
        assert analysis.message == "final failure"


class TestSuggestFix:
    def test_includes_location_hint(self) -> None:
        analysis = BugFixer().analyze(TRACEBACK_IMPORT)
        suggestions = BugFixer().suggest_fix(analysis)
        assert suggestions[-1] == "Inspect 'app.py:12'"

    def test_returns_copy_of_suggestions(self) -> None:
        analysis = BugFixer().analyze("TypeError: wrong")
        suggestions = BugFixer().suggest_fix(analysis)
        assert suggestions == analysis.suggestions
        assert suggestions is not analysis.suggestions


class TestRun:
    def _context(self, tmp_path) -> DeveloperContext:
        config = DeveloperConfig(project_root=str(tmp_path))
        return DeveloperContext(config=config, registry=DeveloperRegistry())

    def test_run_without_failure_raises(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        with pytest.raises(GenerationError, match="A failure description is required"):
            BugFixer().run(ctx, "goal")

    def test_run_records_analysis(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        analysis = BugFixer().run(ctx, "goal", failure=TRACEBACK_IMPORT)
        assert analysis.category == "import"
        assert ctx.stats["bug_category"] == "import"
        assert ctx.stats["bug_error_type"] == "ModuleNotFoundError"
        events = [e.type for e in ctx.bus.history(event_type="bugfix.completed")]
        assert events == ["bugfix.completed"]
        assert ctx.stats.get("bugfix_files_written", 0) == 0

    def test_run_applies_replacement(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        (tmp_path / "app.py").write_text("x = broken", encoding="utf-8")
        analysis = BugFixer().run(
            ctx,
            "goal",
            failure="NameError: name 'broken' is not defined",
            path="app.py",
            replacement="x = 42",
        )
        assert analysis.category == "name"
        assert ctx.stats["bugfix_files_written"] == 1
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "x = 42"

    def test_run_dry_run_does_not_write(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        (tmp_path / "app.py").write_text("x = broken", encoding="utf-8")
        BugFixer().run(
            ctx,
            "goal",
            failure="NameError: name 'broken' is not defined",
            path="app.py",
            replacement="x = 42",
            dry_run=True,
        )
        # The generator reports the would-be write; the file is untouched.
        assert ctx.stats["bugfix_files_written"] == 1
        assert (tmp_path / "app.py").read_text(encoding="utf-8") == "x = broken"
