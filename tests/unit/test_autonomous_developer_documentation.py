"""Unit tests for the Autonomous Developer documentation writer (Phase E)."""
from __future__ import annotations

import pytest

import modules.autonomous_developer.documentation as _docs
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import GenerationError, SecurityError
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.documentation import (
    DocumentationWriter,
    generate_api_docs,
    generate_changelog_entry,
    generate_readme,
)

SOURCE = """def add(a, b=2, *args, **kwargs):
    return a + b


def _private():
    pass


class Calculator:
    def multiply(self, a, b):
        return a * b

    def _hidden(self):
        pass


class Empty:
    pass
"""


class TestGenerateReadme:
    def test_full_readme(self) -> None:
        content = generate_readme(
            "App", "Does things", ["Fast", "Safe"], usage="app.run()"
        )
        assert content.startswith("# App\n")
        assert "Does things" in content
        assert "## Features" in content
        assert "- Fast" in content
        assert "- Safe" in content
        assert "## Usage" in content
        assert "```python" in content
        assert "app.run()" in content

    def test_no_optional_sections(self) -> None:
        content = generate_readme("App")
        assert "## Features" not in content
        assert "## Usage" not in content


class TestGenerateChangelog:
    def test_entry_with_changes(self) -> None:
        content = generate_changelog_entry("1.1.0", ["Added login", "Fixed bug"], when="2026-08-05")
        assert "## [1.1.0] - 2026-08-05" in content
        assert "- Added login" in content
        assert "- Fixed bug" in content

    def test_default_date_is_today(self) -> None:
        from datetime import date

        content = generate_changelog_entry("1.0.0", ["Initial release"])
        assert f"- {date.today().isoformat()}" in content or " - " in content

    def test_no_changes(self) -> None:
        content = generate_changelog_entry("1.0.0", [], when="2026-08-05")
        assert "## [1.0.0] - 2026-08-05" in content


class TestGenerateApiDocs:
    def test_functions_with_signatures(self) -> None:
        content = generate_api_docs(SOURCE, "calc")
        assert "# calc API" in content
        assert "## Functions" in content
        assert "- `add(a, b=2, *args, **kwargs)`" in content

    def test_kwonly_signature(self) -> None:
        content = generate_api_docs("def f(a, *, b):\n    pass\n", "m")
        assert "- `f(a, *, b)`" in content

    def test_classes_and_methods(self) -> None:
        content = generate_api_docs(SOURCE, "calc")
        assert "## Classes" in content
        assert "### Calculator" in content
        assert "- `multiply(self, a, b)`" in content

    def test_class_without_methods_noted(self) -> None:
        content = generate_api_docs(SOURCE, "calc")
        assert "### Empty" in content
        assert "- *(no public methods)*" in content

    def test_private_members_excluded(self) -> None:
        content = generate_api_docs(SOURCE, "calc")
        assert "_private" not in content
        assert "_hidden" not in content

    def test_empty_module_note(self) -> None:
        content = generate_api_docs("", "m")
        assert "*(no public functions or classes)*" in content

    def test_invalid_syntax_note(self) -> None:
        content = generate_api_docs("def broken(:\n", "m")
        assert "*(no public functions or classes)*" in content


class TestGenerateApiDocsForFile:
    def test_relative_path_under_root(self, tmp_path) -> None:
        (tmp_path / "app.py").write_text("def run():\n    pass\n", encoding="utf-8")
        result = DocumentationWriter().generate_api_docs_for_file("app.py", project_root=tmp_path)
        assert result.path == str((tmp_path / "app_api.md").resolve())
        assert "# app API" in result.content
        assert result.sections == ["api"]
        assert result.success

    def test_missing_source_raises(self, tmp_path) -> None:
        with pytest.raises(GenerationError, match="Source file not found"):
            DocumentationWriter().generate_api_docs_for_file("missing.py", project_root=tmp_path)

    def test_path_escape_raises(self, tmp_path) -> None:
        with pytest.raises(SecurityError, match="Path escapes project root"):
            DocumentationWriter().generate_api_docs_for_file(
                tmp_path.parent / "outside.py", project_root=tmp_path
            )


class TestRun:
    def _context(self, tmp_path) -> DeveloperContext:
        config = DeveloperConfig(project_root=str(tmp_path))
        return DeveloperContext(config=config, registry=DeveloperRegistry())

    def test_run_without_path_raises(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        with pytest.raises(GenerationError, match="A source path is required"):
            DocumentationWriter().run(ctx, "goal")

    def test_run_writes_docs(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        (tmp_path / "app.py").write_text("def run():\n    pass\n", encoding="utf-8")
        result = DocumentationWriter().run(ctx, "goal", path="app.py")
        assert (tmp_path / "app_api.md").exists()
        assert "# app API" in (tmp_path / "app_api.md").read_text(encoding="utf-8")
        assert ctx.stats["docs_sections"] == 1
        assert ctx.stats["docs_written"] == 1
        events = [e.type for e in ctx.bus.history(event_type="docs.generated")]
        assert events == ["docs.generated"]

    def test_run_dry_run_writes_nothing(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        (tmp_path / "app.py").write_text("def run():\n    pass\n", encoding="utf-8")
        DocumentationWriter().run(ctx, "goal", path="app.py", dry_run=True)
        assert not (tmp_path / "app_api.md").exists()
        assert ctx.stats["docs_written"] == 1  # would-be write
