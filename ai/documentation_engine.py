from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("superdev.ai.docs")


class DocstringStyle(str, Enum):
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    EPYTEXT = "epytext"


@dataclass
class DocConfig:
    style: DocstringStyle = DocstringStyle.GOOGLE
    include_types: bool = True
    include_exceptions: bool = True
    max_line_length: int = 88
    add_returns: bool = True


@dataclass
class GeneratedDocumentation:
    content: str
    style: DocstringStyle = DocstringStyle.GOOGLE
    original_text: str = ""
    file_path: Optional[str] = None
    changes_made: int = 0
    warnings: list[str] = field(default_factory=list)


DOCSTRING_TEMPLATES: dict[DocstringStyle, dict[str, str]] = {
    DocstringStyle.GOOGLE: {
        "function": '"""{description}\n\nArgs:\n{args}\n\nReturns:\n{returns}\n"""',
        "class": '"""{description}\n\nAttributes:\n{attrs}\n"""',
        "module": '"""{description}\n\nModule Attributes:\n{attrs}\n"""',
    },
    DocstringStyle.NUMPY: {
        "function": '"""{description}\n\nParameters\n----------\n{args}\n\nReturns\n-------\n{returns}\n"""',
        "class": '"""{description}\n\nAttributes\n----------\n{attrs}\n"""',
    },
    DocstringStyle.SPHINX: {
        "function": '"""{description}\n\n:param {arg_name}: {arg_desc}\n:type {arg_name}: {arg_type}\n:returns: {return_desc}\n:rtype: {return_type}\n"""',
        "class": '"""{description}\n\n.. attribute:: {attr_name}\n   {attr_desc}\n"""',
    },
}


class DocumentationEngine:
    def __init__(self, config: Optional[DocConfig] = None) -> None:
        self._config = config or DocConfig()

    def generate_docstring(
        self,
        code: str,
        style: Optional[DocstringStyle] = None,
    ) -> GeneratedDocumentation:
        style = style or self._config.style
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return GeneratedDocumentation(
                content="",
                style=style,
                original_text=code,
                warnings=[f"Syntax error: {exc}"],
            )

        new_code = code
        changes = 0
        warnings: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    docstring = self._generate_function_docstring(node, style)
                    if docstring:
                        insert_pos = node.body[0].lineno if node.body else node.lineno
                        lines = new_code.split("\n")
                        indent = " " * (node.col_offset + 4)
                        doc_lines = [f"{indent}{line}" for line in docstring.split("\n")]
                        for i, dline in enumerate(doc_lines):
                            lines.insert(insert_pos - 1 + i, dline)
                        new_code = "\n".join(lines)
                        changes += 1

            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    docstring = self._generate_class_docstring(node, style)
                    if docstring:
                        insert_pos = node.body[0].lineno if node.body else node.lineno
                        lines = new_code.split("\n")
                        indent = " " * (node.col_offset + 4)
                        doc_lines = [f"{indent}{line}" for line in docstring.split("\n")]
                        for i, dline in enumerate(doc_lines):
                            lines.insert(insert_pos - 1 + i, dline)
                        new_code = "\n".join(lines)
                        changes += 1

        return GeneratedDocumentation(
            content=new_code,
            style=style,
            original_text=code,
            changes_made=changes,
            warnings=warnings,
        )

    def _generate_function_docstring(
        self, node: ast.FunctionDef, style: DocstringStyle
    ) -> Optional[str]:
        func_name = node.name
        description = self._infer_function_description(node)
        args = node.args.args
        returns = node.returns

        if style == DocstringStyle.GOOGLE:
            args_str = "\n".join(
                f"    {a.arg}: Description of {a.arg}."
                for a in args
                if a.arg != "self" and a.arg != "cls"
            )
            return_str = "Description of the return value." if returns else ""
            template = DOCSTRING_TEMPLATES[style]["function"]
            return template.format(description=description, args=args_str or "", returns=return_str)

        elif style == DocstringStyle.NUMPY:
            args_str = "\n".join(
                f"{a.arg} : type\n    Description of {a.arg}."
                for a in args
                if a.arg != "self" and a.arg != "cls"
            )
            return_str = "Description of the return value." if returns else ""
            template = DOCSTRING_TEMPLATES[style]["function"]
            return template.format(description=description, args=args_str or "", returns=return_str)

        elif style == DocstringStyle.SPHINX:
            parts = [description]
            for a in args:
                if a.arg not in ("self", "cls"):
                    parts.append(f":param {a.arg}: Description of {a.arg}.")
                    if a.annotation:
                        parts.append(f":type {a.arg}: {ast.dump(a.annotation)}")
            if returns:
                parts.append(":returns: Description of the return value.")
                parts.append(":rtype: type")
            template = DOCSTRING_TEMPLATES[style]["function"]
            return template.format(description=description, arg_name="arg", arg_desc="desc", arg_type="type", return_desc="desc", return_type="type")

        return None

    def _generate_class_docstring(
        self, node: ast.ClassDef, style: DocstringStyle
    ) -> Optional[str]:
        description = f"{node.name} class."
        attrs = []

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attrs.append(item.target.id)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attrs.append(target.id)

        if style == DocstringStyle.GOOGLE:
            attrs_str = "\n".join(f"    {a}: Description of {a}." for a in attrs)
            return DOCSTRING_TEMPLATES[style]["class"].format(
                description=description, attrs=attrs_str or ""
            )

        elif style == DocstringStyle.NUMPY:
            attrs_str = "\n".join(f"{a} : type\n    Description of {a}." for a in attrs)
            return DOCSTRING_TEMPLATES[style]["class"].format(
                description=description, attrs=attrs_str or ""
            )

        return description

    def _infer_function_description(self, node: ast.FunctionDef) -> str:
        name = node.name
        name_map = {
            "get": f"Retrieve a {name[3:].lower() if len(name) > 3 else 'resource'}.",
            "set": f"Set the {name[3:].lower() if len(name) > 3 else 'value'}.",
            "create": f"Create a new {name[6:].lower() if len(name) > 6 else 'resource'}.",
            "update": f"Update an existing {name[6:].lower() if len(name) > 6 else 'resource'}.",
            "delete": f"Delete a {name[6:].lower() if len(name) > 6 else 'resource'}.",
            "validate": "Validate the input data.",
            "parse": "Parse and process the input.",
            "convert": "Convert between formats.",
            "init": "Initialize the instance.",
        }

        for prefix, desc in name_map.items():
            if name.startswith(prefix):
                return desc

        return f"Execute the {name} operation."

    def generate_readme(
        self,
        project_name: str,
        description: str,
        project_path: Optional[str] = None,
    ) -> str:
        sections: list[str] = []

        sections.append(f"# {project_name}\n")
        if description:
            sections.append(f"{description}\n")

        sections.append("## Installation\n")
        sections.append("```bash\npip install -r requirements.txt\n```\n")

        sections.append("## Quick Start\n")
        sections.append("```python\n# TODO: Add quick start example\n```\n")

        if project_path:
            path = Path(project_path)
            py_files = list(path.rglob("*.py"))
            if py_files:
                sections.append("## Project Structure\n")
                sections.append("```\n")
                for f in sorted(py_files):
                    relative = f.relative_to(path)
                    sections.append(f"{relative}\n")
                sections.append("```\n")

            modules = self._analyze_project_modules(project_path)
            if modules:
                sections.append("## Modules\n")
                for mod_name, mod_desc in modules:
                    sections.append(f"- **{mod_name}**: {mod_desc}\n")
                sections.append("")

        sections.append("## Usage\n")
        sections.append("Refer to the API documentation for detailed usage.\n")

        sections.append("## License\n")
        sections.append("MIT License\n")

        return "".join(sections)

    def _analyze_project_modules(
        self, project_path: str
    ) -> list[tuple[str, str]]:
        modules: list[tuple[str, str]] = []
        path = Path(project_path)

        for py_file in sorted(path.rglob("*.py")):
            if py_file.name == "__init__.py":
                continue
            try:
                code = py_file.read_text(encoding="utf-8")
                tree = ast.parse(code)
                docstring = ast.get_docstring(tree)
                relative = py_file.relative_to(path)
                module_name = str(relative).replace("\\", ".").replace("/", ".").replace(".py", "")
                modules.append((module_name, docstring or "No description"))
            except (SyntaxError, OSError):
                continue

        return modules

    def generate_api_docs(
        self, code: str, module_name: str = ""
    ) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return f"# API Documentation\n\nError: {exc}\n"

        parts = [f"# {module_name} API Documentation\n" if module_name else "# API Documentation\n"]

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or "No description."
                parts.append(f"## Class: {node.name}\n")
                parts.append(f"{doc}\n")

                methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                for method in methods:
                    method_doc = ast.get_docstring(method) or "No description."
                    sig = f"{method.name}("
                    args = [a.arg for a in method.args.args if a.arg not in ("self", "cls")]
                    sig += ", ".join(args) + ")"
                    parts.append(f"### `{sig}`\n")
                    parts.append(f"{method_doc}\n")

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if isinstance(getattr(node, "parent", None), ast.Module):
                    doc = ast.get_docstring(node) or "No description."
                    sig = f"{node.name}("
                    args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
                    sig += ", ".join(args) + ")"
                    parts.append(f"## `{sig}`\n")
                    parts.append(f"{doc}\n")

        return "\n".join(parts)

    def enhance_comments(self, code: str) -> GeneratedDocumentation:
        lines = code.split("\n")
        new_lines: list[str] = []
        changes = 0
        warnings: list[str] = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith("#") and not stripped.startswith("#!") and not stripped.startswith("# -*-"):
                if len(stripped) < 15 and not stripped.endswith("."):
                    prev_line = lines[i - 1].strip() if i > 0 else ""
                    if prev_line and not prev_line.startswith("#"):
                        suggestion = self._suggest_comment(prev_line)
                        if suggestion:
                            new_lines[-1] = f"    # {suggestion}" if line.startswith(" ") else f"# {suggestion}"
                            changes += 1
                            continue

            new_lines.append(line)

        return GeneratedDocumentation(
            content="\n".join(new_lines),
            original_text=code,
            changes_made=changes,
            warnings=warnings,
        )

    def _suggest_comment(self, code_line: str) -> Optional[str]:
        if "=" in code_line and "def " not in code_line and "import " not in code_line:
            return "Initialize or assign value"
        if "for " in code_line:
            return "Iterate over collection"
        if "if " in code_line:
            return "Conditional check"
        if "return " in code_line:
            return "Return result"
        if "import " in code_line:
            return "Import module"
        if "class " in code_line:
            return "Class definition"
        if "def " in code_line:
            return "Function definition"
        if "try:" in code_line:
            return "Exception handling block"
        if "with " in code_line:
            return "Context manager"
        return None

    def format_markdown(self, content: str) -> str:
        lines = content.split("\n")
        formatted: list[str] = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                formatted.append(line)
                continue

            if not in_code_block:
                if line.startswith("#") and not line.startswith("##"):
                    formatted.append(line.strip())
                    formatted.append("")
                    continue

                if line.strip() and not line.startswith("-") and not line.startswith("*") and not line.strip().isdigit():
                    if len(line) > self._config.max_line_length:
                        words = line.split()
                        current = ""
                        for word in words:
                            if len(current) + len(word) + 1 > self._config.max_line_length:
                                formatted.append(current)
                                current = word
                            else:
                                current = f"{current} {word}".strip()
                        if current:
                            formatted.append(current)
                        continue

            formatted.append(line)

        return "\n".join(formatted)

    def generate_module_docs(
        self, code: str, module_name: str = ""
    ) -> str:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return ""

        docstring = ast.get_docstring(tree) or f"The {module_name or 'unknown'} module."
        classes = []
        functions = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)

        parts = [
            f"# Module: {module_name}\n" if module_name else "",
            f"{docstring}\n",
        ]

        if classes:
            parts.append(f"## Classes\n")
            for cls in classes:
                parts.append(f"- `{cls}`\n")
            parts.append("")

        if functions:
            parts.append(f"## Functions\n")
            for func in functions:
                parts.append(f"- `{func}()`\n")
            parts.append("")

        return "".join(parts)
