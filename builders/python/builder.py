"""Python Builder — renders the ``builders/python/src/{{project_name}}`` template tree.

Unlike the other builders (which generate code from inline f-strings), this
builder copies the on-disk template package and renames it for the target
project. The template files use the placeholder identifier ``project_name``
in import statements (kept as a valid Python identifier so the template tree
itself stays importable/lintable), and this builder rewrites those imports to
the real project slug.

Example:
    config.project_name = "My App"  →  slug "my-app"
    ``from project_name.config import get_settings`` becomes
    ``from my_app.config import get_settings`` (dots are invalid in module
    names, so hyphens are converted to underscores for imports).
"""

from __future__ import annotations

import os
import time
from pathlib import Path

from ..base import (
    BaseBuilder,
    BuildConfig,
    BuildResult,
    FrameworkType,
    GeneratedFile,
)

# Root of the template tree shipped with this package:
# builders/python/src/{{project_name}}/...
_TEMPLATE_ROOT = Path(__file__).resolve().parent / "src" / "{{project_name}}"

# Placeholder used inside template files. It is a plain identifier (not
# Jinja syntax) so the template tree compiles as regular Python.
_PLACEHOLDER = "project_name"


def _python_slug(project_slug: str) -> str:
    """Convert a project slug into a valid Python package name."""
    return project_slug.replace("-", "_").replace(" ", "_")


class PythonBuilder(BaseBuilder):
    """Generates a full-featured Python/FastAPI package from the template tree."""

    name = "python"
    description = "Generates a Python/FastAPI package from the {{project_name}} template"
    framework = FrameworkType.PYTHON

    async def build(self, config: BuildConfig) -> BuildResult:
        start = time.time()
        slug = config.project_slug
        py_slug = _python_slug(slug)

        try:
            files = self._render_template_tree(config, slug, py_slug)

            elapsed_ms = round((time.time() - start) * 1000, 2)
            return BuildResult(
                builder_name=self.name,
                project_name=config.project_name,
                project_slug=slug,
                total_files=len(files),
                files=files,
                build_duration_ms=elapsed_ms,
            )
        except Exception as e:
            return BuildResult(
                builder_name=self.name,
                project_name=config.project_name,
                project_slug=slug,
                error=str(e),
                build_duration_ms=round((time.time() - start) * 1000, 2),
            )

    def _render_template_tree(self, config: BuildConfig, slug: str, py_slug: str) -> list[GeneratedFile]:
        """Walk the template dir and render every file with the project names."""
        if not _TEMPLATE_ROOT.is_dir():
            raise FileNotFoundError(
                f"Template tree not found: {_TEMPLATE_ROOT}. The builders/python package appears to be incomplete."
            )

        rendered: list[GeneratedFile] = []

        for dirpath, dirnames, filenames in os.walk(_TEMPLATE_ROOT):
            # Never descend into caches or the summary artifacts.
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__",) and d != "mantis-summary.md"]
            for filename in filenames:
                if filename == "mantis-summary.md":
                    continue
                template_path = Path(dirpath) / filename
                rel_path = template_path.relative_to(_TEMPLATE_ROOT).as_posix()

                # The template root IS the package directory, so every rendered
                # file lands directly under the real package name: main.py → <py_slug>/main.py
                out_rel = self._rename_placeholders_in_path(rel_path, slug, py_slug)
                out_rel = f"{py_slug}/{out_rel}"

                content = template_path.read_text(encoding="utf-8")
                content = self._render_content(content, config, slug, py_slug)

                rendered.append(self._make_file(f"src/{out_rel}", content))

        # Companion files that make the package installable/runnable.
        rendered.extend(self._companion_files(config, slug, py_slug))
        return rendered

    def _rename_placeholders_in_path(self, rel_path: str, slug: str, py_slug: str) -> str:
        """Replace any remaining placeholder occurrences in path segments."""
        return rel_path.replace("{{project_name}}", py_slug).replace("{{project_slug}}", slug)

    def _render_content(self, content: str, config: BuildConfig, slug: str, py_slug: str) -> str:
        """Apply template substitutions to file content."""
        content = content.replace("{{project_name}}", config.project_name)
        content = content.replace("{{project_slug}}", slug)
        # Rewrite placeholder package imports: project_name.config → <py_slug>.config
        content = content.replace(f"from {_PLACEHOLDER}.", f"from {py_slug}.").replace(
            f"import {_PLACEHOLDER}", f"import {py_slug}"
        )
        # String references like "<py_slug>.main:app" for uvicorn.
        content = content.replace(f'"{_PLACEHOLDER}.main:app"', f'"{py_slug}.main:app"')
        return content

    def _companion_files(self, config: BuildConfig, slug: str, py_slug: str) -> list[GeneratedFile]:
        """Generate pyproject/README/env files alongside the rendered package."""
        files: list[GeneratedFile] = []

        files.append(
            self._make_file(
                "src/pyproject.toml",
                f'''[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{slug}"
version = "0.1.0"
description = "{config.project_name}"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "aiosqlite>=0.19.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "structlog>=24.1.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["{py_slug}*"]
''',
            )
        )

        files.append(
            self._make_file(
                "src/README.md",
                f"""# {config.project_name}

Python/FastAPI service generated by the SuperDev Python Builder.

## Quick start

```bash
pip install -e src
uvicorn {py_slug}.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health
""",
            )
        )

        files.append(
            self._make_file(
                "src/.env.example",
                f'''APP_NAME="{config.project_name}"
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET_KEY=change-me-in-production
''',
            )
        )

        return files
