"""Test generator — AST-driven pytest scaffolding.

Parses a Python module's public functions and class methods and produces a
deterministic pytest file: one ``test_<func>`` per function and a
``Test<Class>`` group per class, each with an import/attribute guard and a
placeholder assertion for the developer to fill in.
"""
from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.security_rules import SecurityRules
from modules.autonomous_developer.core.exceptions import GenerationError, SecurityError
from modules.autonomous_developer.core.models import FileChange
from modules.autonomous_developer.generator.generator import CodeGenerator

_NON_IDENTIFIER = re.compile(r"[^A-Za-z0-9_]")


@dataclass(slots=True)
class TestGenerationResult:
    """Outcome of generating tests for one module."""

    source_path: str = ""
    test_path: str = ""
    content: str = ""
    generated_tests: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "test_path": self.test_path,
            "generated_tests": self.generated_tests,
            "errors": list(self.errors),
        }


def sanitize_module_name(module_name: str) -> str:
    """Return a valid importable module identifier from ``module_name``."""
    name = _NON_IDENTIFIER.sub("_", (module_name or "").split(".")[-1])
    if not name:
        return "module"
    if not re.match(r"[A-Za-z_]", name):
        name = f"_{name}"
    return name


def tests_filename(module_name: str) -> str:
    """Return the pytest file name for a module, e.g. ``test_app.py``.

    Named ``tests_filename`` (not ``test_*``) so the name is never picked up
    by pytest's ``test_*`` collection when imported into a test module.
    """
    return f"test_{sanitize_module_name(module_name)}.py"


def _collect(source: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Return (function names, [(class name, [method names])]) in source order."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], []
    funcs = [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    classes = [
        (
            node.name,
            [
                member.name
                for member in node.body
                if isinstance(member, ast.FunctionDef) and not member.name.startswith("_")
            ],
        )
        for node in tree.body
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
    ]
    return funcs, classes


def _render(module_name: str, funcs: list[str], classes: list[tuple[str, list[str]]]) -> tuple[str, int]:
    lines = [
        f'"""Auto-generated tests for {module_name}."""',
        "from __future__ import annotations",
        "",
        "import pytest",
        "",
        f"import {module_name} as _module",
        "",
    ]
    count = 0
    for func in funcs:
        count += 1
        lines.extend(
            [
                f"def test_{func}():",
                f'    """Generated stub for {func}."""',
                f'    assert hasattr(_module, "{func}")',
                "",
            ]
        )
    for class_name, methods in classes:
        lines.extend(
            [
                f"class Test{class_name}:",
                f'    """Generated test group for {class_name}."""',
                "",
            ]
        )
        if methods:
            for method in methods:
                count += 1
                lines.extend(
                    [
                        f"    def test_{method}(self):",
                        f'        """Generated stub for {class_name}.{method}."""',
                        f'        assert hasattr(_module.{class_name}, "{method}")',
                        "",
                    ]
                )
        else:
            count += 1
            lines.extend(
                [
                    "    def test_class_exists(self):",
                    f'        """Generated stub for {class_name}."""',
                    f'        assert _module.{class_name} is not None',
                    "",
                ]
            )
    if count == 0:
        count = 1
        lines.extend(
            [
                "def test_module_imports():",
                "    \"\"\"Generated stub: the module must be importable.\"\"\"",
                "    assert _module is not None",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n", count


class TestGenerator:
    """Generates deterministic pytest scaffolding from source modules."""

    def __init__(
        self,
        config: GeneratorConfig | None = None,
        security: SecurityRules | None = None,
    ) -> None:
        self.config = config or GeneratorConfig()
        self.security = security or SecurityRules()

    def generate_tests(self, source: str, module_name: str = "module") -> tuple[str, int]:
        """Return (test file content, number of generated tests)."""
        name = sanitize_module_name(module_name)
        funcs, classes = _collect(source)
        return _render(name, funcs, classes)

    def generate_for_file(
        self, path: str | Path, *, project_root: str | Path | None = None
    ) -> TestGenerationResult:
        """Generate tests for the module at ``path``.

        Relative paths resolve against ``project_root`` when given; absolute
        paths are used as-is but must stay inside the root.
        """
        root = Path(project_root).resolve() if project_root is not None else None
        raw = Path(path)
        source_path = (root / raw).resolve() if root is not None else raw.resolve()
        if root is not None:
            try:
                source_path.relative_to(root)
            except ValueError:
                raise SecurityError(f"Path escapes project root: {path}")
        if not source_path.exists():
            raise GenerationError(f"Source file not found: {path}")
        module_name = sanitize_module_name(source_path.stem)
        content, count = self.generate_tests(
            source_path.read_text(encoding=self.config.encoding), module_name
        )
        test_path = source_path.parent / tests_filename(module_name)
        return TestGenerationResult(
            source_path=str(source_path),
            test_path=str(test_path),
            content=content,
            generated_tests=count,
        )

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> TestGenerationResult:
        """Runtime component entry point.

        Requires ``path`` (the source module). Writes the generated test file
        through the code generator (relative path under the project root).
        """
        path = kwargs.get("path")
        if not path:
            raise GenerationError("A source path is required to generate tests")
        result = self.generate_for_file(path, project_root=ctx.config.project_root)
        root = Path(ctx.config.project_root).resolve()
        rel_test_path = os.path.relpath(Path(result.test_path).resolve(), root)
        generator = CodeGenerator()
        write = generator.apply_changes(
            [FileChange(path=rel_test_path, content=result.content)],
            project_root=root,
            dry_run=bool(kwargs.get("dry_run", False)),
        )
        if write.errors:
            result.errors.extend(entry["error"] for entry in write.errors)
        ctx.record("tests_generated", result.generated_tests)
        ctx.record("test_file", result.test_path)
        ctx.record("test_written", len(write.written))
        ctx.publish(
            "tests.generated",
            {
                "test_path": result.test_path,
                "generated": result.generated_tests,
                "written": len(write.written),
            },
        )
        return result
