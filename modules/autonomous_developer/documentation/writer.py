"""Documentation writer — deterministic markdown documentation generation.

Produces README scaffolds, changelog entries and AST-driven API reference
docs for Python modules, and writes them through the code generator so all
write safety (path checks, backups, atomic writes) applies.
"""
from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.security_rules import SecurityRules
from modules.autonomous_developer.core.exceptions import GenerationError, SecurityError
from modules.autonomous_developer.core.models import FileChange
from modules.autonomous_developer.generator.generator import CodeGenerator


@dataclass(slots=True)
class DocumentationResult:
    """Outcome of a documentation generation run."""

    path: str = ""
    content: str = ""
    sections: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "sections": list(self.sections),
            "errors": list(self.errors),
        }


def generate_readme(
    name: str,
    description: str = "",
    features: list[str] | None = None,
    usage: str = "",
) -> str:
    """Build a markdown README scaffold for ``name``."""
    lines = [f"# {name}", ""]
    if description:
        lines.extend([description, ""])
    feature_list = features or []
    if feature_list:
        lines.append("## Features")
        lines.append("")
        for feature in feature_list:
            lines.append(f"- {feature}")
        lines.append("")
    if usage:
        lines.extend(["## Usage", "", "```python", usage, "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def generate_changelog_entry(version: str, changes: list[str], when: str = "") -> str:
    """Build a markdown changelog entry for ``version``."""
    label = when or date.today().isoformat()
    lines = [f"## [{version}] - {label}", ""]
    for change in changes or []:
        lines.append(f"- {change}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _signature(node: ast.FunctionDef) -> str:
    """Render a callable's signature deterministically from its AST node."""
    positional = list(node.args.posonlyargs) + list(node.args.args)
    defaults = [None] * (len(positional) - len(node.args.defaults)) + list(node.args.defaults)
    parts = []
    for arg, default in zip(positional, defaults):
        rendered = arg.arg
        if default is not None:
            rendered += f"={ast.unparse(default)}"
        parts.append(rendered)
    if node.args.vararg:
        parts.append("*" + node.args.vararg.arg)
    elif node.args.kwonlyargs:
        parts.append("*")
    parts.extend(arg.arg for arg in node.args.kwonlyargs)
    if node.args.kwarg:
        parts.append("**" + node.args.kwarg.arg)
    return f"{node.name}({', '.join(parts)})"


def generate_api_docs(source: str, module_name: str = "module") -> str:
    """Build a markdown API reference from a module's public surface."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        tree = None
    name = re.sub(r"[^A-Za-z0-9_]", "_", (module_name or "").split(".")[-1]) or "module"
    lines = [f"# {name} API", ""]

    funcs = (
        [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        ]
        if tree is not None
        else []
    )
    if funcs:
        lines.append("## Functions")
        lines.append("")
        for node in funcs:
            lines.append(f"- `{_signature(node)}`")
        lines.append("")

    classes = (
        [
            (node.name, [m for m in node.body if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")])
            for node in tree.body
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
        ]
        if tree is not None
        else []
    )
    if classes:
        lines.append("## Classes")
        lines.append("")
        for class_name, methods in classes:
            lines.append(f"### {class_name}")
            lines.append("")
            if methods:
                for method in methods:
                    lines.append(f"- `{_signature(method)}`")
            else:
                lines.append("- *(no public methods)*")
            lines.append("")
    if not funcs and not classes:
        lines.extend(["*(no public functions or classes)*", ""])
    return "\n".join(lines).rstrip() + "\n"


class DocumentationWriter:
    """Generates markdown documentation for modules and goals."""

    def __init__(
        self,
        config: GeneratorConfig | None = None,
        security: SecurityRules | None = None,
    ) -> None:
        self.config = config or GeneratorConfig()
        self.security = security or SecurityRules()

    def generate_api_docs_for_file(
        self, path: str | Path, *, project_root: str | Path | None = None
    ) -> DocumentationResult:
        """Generate an API reference for the module at ``path``."""
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
        module_name = re.sub(r"[^A-Za-z0-9_]", "_", source_path.stem) or "module"
        content = generate_api_docs(source_path.read_text(encoding=self.config.encoding), module_name)
        doc_path = source_path.parent / f"{source_path.stem}_api.md"
        return DocumentationResult(
            path=str(doc_path), content=content, sections=["api"]
        )

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> DocumentationResult:
        """Runtime component entry point.

        Requires ``path`` (the source module). Writes ``<stem>_api.md`` next to
        the source through the code generator (relative path under the root).
        """
        path = kwargs.get("path")
        if not path:
            raise GenerationError("A source path is required to generate documentation")
        result = self.generate_api_docs_for_file(path, project_root=ctx.config.project_root)
        root = Path(ctx.config.project_root).resolve()
        rel_doc_path = os.path.relpath(Path(result.path).resolve(), root)
        write = CodeGenerator().apply_changes(
            [FileChange(path=rel_doc_path, content=result.content)],
            project_root=root,
            dry_run=bool(kwargs.get("dry_run", False)),
        )
        if write.errors:
            result.errors.extend(entry["error"] for entry in write.errors)
        ctx.record("docs_sections", len(result.sections))
        ctx.record("docs_written", len(write.written))
        ctx.publish(
            "docs.generated",
            {
                "doc_path": result.path,
                "sections": result.sections,
                "written": len(write.written),
            },
        )
        return result
