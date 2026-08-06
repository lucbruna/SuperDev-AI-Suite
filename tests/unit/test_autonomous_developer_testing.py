"""Unit tests for the Autonomous Developer test generator (Phase D)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import GenerationError, SecurityError
from modules.autonomous_developer.core.registry import DeveloperRegistry
import modules.autonomous_developer.testing as _testing
from modules.autonomous_developer.testing import sanitize_module_name, tests_filename

SOURCE = """def helper():
    return 1


def add(a, b):
    return a + b


def _private():
    return "hidden"


class Calculator:
    def add(self, a, b):
        return a + b

    def _hidden(self):
        return None
"""


class TestSanitize:
    def test_plain_name(self) -> None:
        assert sanitize_module_name("app") == "app"

    def test_dotted_name_uses_last_segment(self) -> None:
        assert sanitize_module_name("pkg.module") == "module"

    def test_non_identifier_chars_replaced(self) -> None:
        assert sanitize_module_name("my-module") == "my_module"

    def test_empty_falls_back_to_module(self) -> None:
        assert sanitize_module_name("") == "module"

    def test_leading_digit_prefixed(self) -> None:
        assert sanitize_module_name("1abc") == "_1abc"

    def test_tests_filename(self) -> None:
        assert tests_filename("app") == "test_app.py"
        assert tests_filename("pkg.util") == "test_util.py"


class TestGenerateTests:
    def test_functions_and_classes_emitted(self) -> None:
        content, count = _testing.TestGenerator().generate_tests(SOURCE, "calc")
        assert "import calc as _module" in content
        assert "def test_helper():" in content
        assert "def test_add():" in content
        assert 'assert hasattr(_module, "add")' in content
        assert "class TestCalculator:" in content
        assert "def test_add(self):" in content
        assert 'assert hasattr(_module.Calculator, "add")' in content
        assert count == 3  # helper + add + Calculator.add

    def test_private_members_excluded(self) -> None:
        content, _count = _testing.TestGenerator().generate_tests(SOURCE, "calc")
        assert "test__private" not in content
        assert "test__hidden" not in content

    def test_class_without_methods_gets_exists_stub(self) -> None:
        content, count = _testing.TestGenerator().generate_tests(
            "class Marker:\n    pass\n", "marker"
        )
        assert "class TestMarker:" in content
        assert "def test_class_exists(self):" in content
        assert count == 1

    def test_empty_source_gets_import_stub(self) -> None:
        content, count = _testing.TestGenerator().generate_tests("", "empty")
        assert "def test_module_imports():" in content
        assert "assert _module is not None" in content
        assert count == 1

    def test_invalid_syntax_gets_import_stub(self) -> None:
        content, count = _testing.TestGenerator().generate_tests("def broken(:\n", "broken")
        assert "def test_module_imports():" in content
        assert count == 1

    def test_generated_file_roundtrips(self) -> None:
        content, _count = _testing.TestGenerator().generate_tests(SOURCE, "calc")
        compile(content, "<generated>", "exec")  # valid Python


class TestGenerateForFile:
    def test_generates_next_to_source(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("def run():\n    pass\n", encoding="utf-8")
        result = _testing.TestGenerator().generate_for_file("app.py", project_root=tmp_path)
        assert result.source_path == str((tmp_path / "app.py").resolve())
        assert result.test_path == str((tmp_path / "test_app.py").resolve())
        assert "import app as _module" in result.content
        assert result.generated_tests == 1
        assert result.success

    def test_absolute_path_inside_root_accepted(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("x = 1", encoding="utf-8")
        result = _testing.TestGenerator().generate_for_file(tmp_path / "app.py", project_root=tmp_path)
        # No public functions/classes -> the import stub test is generated.
        assert result.generated_tests == 1
        assert "def test_module_imports():" in result.content

    def test_missing_source_raises(self, tmp_path) -> None:
        with pytest.raises(GenerationError, match="Source file not found"):
            _testing.TestGenerator().generate_for_file("missing.py", project_root=tmp_path)

    def test_path_escape_raises(self, tmp_path) -> None:
        with pytest.raises(SecurityError, match="Path escapes project root"):
            _testing.TestGenerator().generate_for_file(tmp_path.parent / "outside.py", project_root=tmp_path)


class TestRun:
    def _context(self, tmp_path) -> DeveloperContext:
        config = DeveloperConfig(project_root=str(tmp_path))
        return DeveloperContext(config=config, registry=DeveloperRegistry())

    def test_run_without_path_raises(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        with pytest.raises(GenerationError, match="A source path is required"):
            _testing.TestGenerator().run(ctx, "goal")

    def test_run_writes_test_file(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        (tmp_path / "app.py").write_text("def run():\n    pass\n", encoding="utf-8")
        result = _testing.TestGenerator().run(ctx, "goal", path="app.py")
        assert result.generated_tests == 1
        assert (tmp_path / "test_app.py").exists()
        assert "import app as _module" in (tmp_path / "test_app.py").read_text(encoding="utf-8")
        assert ctx.stats["tests_generated"] == 1
        assert ctx.stats["test_written"] == 1
        events = [e.type for e in ctx.bus.history(event_type="tests.generated")]
        assert events == ["tests.generated"]

    def test_run_dry_run_writes_nothing(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        (tmp_path / "app.py").write_text("def run():\n    pass\n", encoding="utf-8")
        _testing.TestGenerator().run(ctx, "goal", path="app.py", dry_run=True)
        assert not (tmp_path / "test_app.py").exists()
        # The generator reports would-be writes even in dry-run mode.
        assert ctx.stats["test_written"] == 1
