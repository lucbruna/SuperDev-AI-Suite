from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any


class AutoDocGenerator:
    def __init__(self, root_path: str | None = None):
        self._root = Path(root_path) if root_path else Path.cwd()
        self._output: dict[str, Any] = {}
        self._CONFIG = {
            "extensions": {".py": self._parse_python, ".js": None, ".ts": None, ".tsx": None, ".md": None},
            "max_file_size": 50000,
            "max_files": 100,
        }

    def _parse_python(self, filepath: Path) -> dict[str, Any]:
        try:
            with open(filepath, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except (SyntaxError, UnicodeDecodeError):
            return {"error": "Could not parse"}
        classes = []
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                doc = ast.get_docstring(node) or ""
                classes.append({"name": node.name, "methods": methods, "doc": doc[:200]})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node) or ""
                functions.append({"name": node.name, "args": [a.arg for a in node.args.args], "doc": doc[:200]})
        return {"classes": classes, "functions": functions, "total_lines": self._count_lines(filepath)}

    def _count_lines(self, filepath: Path) -> int:
        try:
            with open(filepath, encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def generate(self, path: str | None = None) -> dict[str, Any]:
        search_path = Path(path) if path else self._root
        self._output = {
            "project": search_path.name,
            "path": str(search_path.resolve()),
            "generated_at": __import__("datetime").datetime.now().isoformat(),
            "modules": {},
            "summary": {},
        }
        files_scanned = 0
        for filepath in sorted(search_path.rglob("*")):
            if not filepath.is_file():
                continue
            if filepath.suffix not in self._CONFIG["extensions"]:
                continue
            if filepath.stat().st_size > self._CONFIG["max_file_size"]:
                continue
            if files_scanned >= self._CONFIG["max_files"]:
                break
            rel_path = str(filepath.relative_to(search_path))
            parser = self._CONFIG["extensions"][filepath.suffix]
            if parser:
                result = parser(filepath)
                self._output["modules"][rel_path] = result
            else:
                self._output["modules"][rel_path] = {"lines": self._count_lines(filepath)}
            files_scanned += 1
        self._compute_summary()
        return self._output

    def _compute_summary(self):
        total_files = len(self._output["modules"])
        total_lines = sum(m.get("total_lines", 0) for m in self._output["modules"].values() if isinstance(m, dict))
        total_classes = sum(len(m.get("classes", [])) for m in self._output["modules"].values() if isinstance(m, dict))
        total_functions = sum(len(m.get("functions", [])) for m in self._output["modules"].values() if isinstance(m, dict))
        self._output["summary"] = {
            "files": total_files,
            "lines": total_lines,
            "classes": total_classes,
            "functions": total_functions,
            "python_files": sum(1 for k, v in self._output["modules"].items() if k.endswith(".py") and isinstance(v, dict) and "classes" in v),
        }

    def to_markdown(self) -> str:
        lines = [f"# {self._output['project']} Documentation", f"Generated: {self._output['generated_at']}", ""]
        s = self._output["summary"]
        lines.append(f"## Summary\n- Files: {s['files']}\n- Lines: {s['lines']}\n- Classes: {s['classes']}\n- Functions: {s['functions']}\n")
        lines.append("## Modules\n")
        for mod_path, mod_data in sorted(self._output["modules"].items()):
            if not isinstance(mod_data, dict):
                continue
            lines.append(f"### {mod_path}")
            if "classes" in mod_data and mod_data["classes"]:
                lines.append("#### Classes")
                for cls in mod_data["classes"]:
                    doc_line = cls["doc"].split("\n")[0] if cls["doc"] else "No docstring"
                    lines.append(f"- `{cls['name']}`: {doc_line}")
                    if cls["methods"]:
                        for m in cls["methods"]:
                            lines.append(f"  - `{m}()`")
            if "functions" in mod_data and mod_data["functions"]:
                lines.append("#### Functions")
                for fn in mod_data["functions"]:
                    doc_line = fn["doc"].split("\n")[0] if fn["doc"] else "No docstring"
                    args = ", ".join(fn["args"])
                    lines.append(f"- `{fn['name']}({args})`: {doc_line}")
            if "error" in mod_data:
                lines.append(f"- Parse error: {mod_data['error']}")
            lines.append("")
        return "\n".join(lines)

    def save(self, output_path: str, fmt: str = "md") -> str:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "md":
            content = self.to_markdown()
        else:
            import json
            content = json.dumps(self._output, indent=2, default=str)
        output_file.write_text(content, encoding="utf-8")
        return str(output_file)