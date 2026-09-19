"""Unit tests for the PythonBuilder ({{project_name}} template renderer)."""

from __future__ import annotations

import py_compile
from pathlib import Path

import pytest

from builders.base import BuildConfig, FrameworkType
from builders.python.builder import PythonBuilder, _python_slug


@pytest.fixture
def builder() -> PythonBuilder:
    return PythonBuilder()


def _config(name: str = "Minha Aplicacao Incrivel") -> BuildConfig:
    return BuildConfig(project_name=name, framework=FrameworkType.PYTHON)


class TestPythonSlug:
    def test_hyphens_become_underscores(self) -> None:
        assert _python_slug("my-app") == "my_app"

    def test_spaces_become_underscores(self) -> None:
        assert _python_slug("my app") == "my_app"


@pytest.mark.asyncio
class TestPythonBuilderBuild:
    async def test_build_succeeds(self, builder: PythonBuilder) -> None:
        result = await builder.build(_config())
        assert result.error == ""
        assert result.builder_name == "python"
        assert result.project_slug == "minha-aplicacao-incrivel"
        assert result.total_files > 0
        assert result.build_duration_ms >= 0

    async def test_build_renders_package_dir_with_python_slug(
        self, builder: PythonBuilder, tmp_path: Path
    ) -> None:
        result = await builder.build(_config())
        builder._write_files(str(tmp_path), result.files)
        pkg = tmp_path / "src" / "minha_aplicacao_incrivel"
        assert pkg.is_dir()
        assert (pkg / "main.py").is_file()
        assert (pkg / "config.py").is_file()

    async def test_companion_files_generated(
        self, builder: PythonBuilder, tmp_path: Path
    ) -> None:
        result = await builder.build(_config())
        builder._write_files(str(tmp_path), result.files)
        src = tmp_path / "src"
        assert (src / "pyproject.toml").is_file()
        assert (src / "README.md").is_file()
        assert (src / ".env.example").is_file()

    async def test_companion_files_render_project_name(
        self, builder: PythonBuilder, tmp_path: Path
    ) -> None:
        result = await builder.build(_config())
        builder._write_files(str(tmp_path), result.files)
        readme = (tmp_path / "src" / "README.md").read_text(encoding="utf-8")
        assert "Minha Aplicacao Incrivel" in readme
        pyproject = (tmp_path / "src" / "pyproject.toml").read_text(encoding="utf-8")
        assert 'name = "minha-aplicacao-incrivel"' in pyproject

    async def test_all_generated_python_compiles(
        self, builder: PythonBuilder, tmp_path: Path
    ) -> None:
        result = await builder.build(_config())
        builder._write_files(str(tmp_path), result.files)
        for py in (tmp_path / "src").rglob("*.py"):
            py_compile.compile(str(py), doraise=True)

    async def test_placeholder_imports_rewritten(
        self, builder: PythonBuilder, tmp_path: Path
    ) -> None:
        result = await builder.build(_config())
        builder._write_files(str(tmp_path), result.files)
        main = (tmp_path / "src" / "minha_aplicacao_incrivel" / "main.py").read_text(
            encoding="utf-8"
        )
        assert "from minha_aplicacao_incrivel.config import" in main
        assert "from project_name." not in main
        assert "{{project_name}}" not in main

    async def test_uvicorn_target_rewritten(
        self, builder: PythonBuilder, tmp_path: Path
    ) -> None:
        result = await builder.build(_config())
        builder._write_files(str(tmp_path), result.files)
        main = (tmp_path / "src" / "minha_aplicacao_incrivel" / "main.py").read_text(
            encoding="utf-8"
        )
        assert '"minha_aplicacao_incrivel.main:app"' in main

    async def test_no_template_caches_in_output(
        self, builder: PythonBuilder, tmp_path: Path
    ) -> None:
        result = await builder.build(_config())
        paths = [f.path for f in result.files]
        assert not any("__pycache__" in p for p in paths)
        assert not any("mantis-summary.md" in p for p in paths)

    async def test_custom_project_name(self, builder: PythonBuilder, tmp_path: Path) -> None:
        result = await builder.build(_config("My Cool Tool"))
        assert result.project_slug == "my-cool-tool"
        builder._write_files(str(tmp_path), result.files)
        pkg = tmp_path / "src" / "my_cool_tool"
        assert pkg.is_dir()
        main = (pkg / "main.py").read_text(encoding="utf-8")
        assert "from my_cool_tool.config import" in main

    async def test_missing_template_tree_reports_error(
        self, builder: PythonBuilder, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import builders.python.builder as mod

        monkeypatch.setattr(mod, "_TEMPLATE_ROOT", Path("Z:/definitely/not/here"))
        result = await builder.build(_config())
        assert result.error != ""
        assert "Template tree not found" in result.error
