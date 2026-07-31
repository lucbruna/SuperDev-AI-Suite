from __future__ import annotations

import ast
import os
import textwrap
from typing import Any


class ExtractFunctionRefactor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    async def extract_function(
        self, filepath: str, start_line: int, end_line: int, new_function_name: str
    ) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {"success": False, "error": f"File not found: {filepath}"}
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
        if start_line < 1 or end_line > len(lines):
            return {
                "success": False,
                "error": f"Line range {start_line}-{end_line} out of bounds (file has {len(lines)} lines)",
            }
        extracted_lines = lines[start_line - 1 : end_line]
        extracted_code = "".join(extracted_lines)
        len(extracted_lines[0]) - len(extracted_lines[0].lstrip()) if extracted_lines else 0
        dedented = textwrap.dedent(extracted_code)
        new_function = f'def {new_function_name}():\n    """Extracted function."""\n'
        for line in dedented.split("\n"):
            if line.strip():
                new_function += f"    {line}\n"
        new_lines = (
            lines[: start_line - 1]
            + [new_function]
            + [f"# TODO: Replace with {new_function_name}() call\n"]
            + lines[end_line:]
        )
        if not self.dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        return {
            "success": True,
            "filepath": filepath,
            "new_function": new_function_name,
            "extracted_lines": end_line - start_line + 1,
            "start_line": start_line,
            "end_line": end_line,
            "dry_run": self.dry_run,
        }

    async def extract_variable(self, filepath: str, line: int, variable_name: str, expression: str) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {"success": False, "error": f"File not found: {filepath}"}
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        new_content = content.replace(expression, variable_name, 1)
        insert_line = f"{variable_name} = {expression}\n"
        new_lines = new_content.split("\n")
        new_lines.insert(line - 1, insert_line)
        new_content = "\n".join(new_lines)
        if not self.dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
        return {
            "success": True,
            "filepath": filepath,
            "variable_name": variable_name,
            "expression": expression,
            "line": line,
            "dry_run": self.dry_run,
        }

    async def inline_function(self, filepath: str, function_name: str) -> dict[str, Any]:
        if not os.path.exists(filepath):
            return {"success": False, "error": f"File not found: {filepath}"}
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {"success": False, "error": f"Syntax error: {e}"}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                body = node.body
                ast.get_source_segment(content, body[0]) if body else ""
                occurrences = content.count(f"{function_name}(")
                if not self.dry_run:
                    func_start = node.lineno
                    func_end = node.end_lineno or func_start
                    lines = content.split("\n")
                    new_lines = lines[: func_start - 1] + lines[func_end:]
                    new_content = "\n".join(new_lines)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                return {
                    "success": True,
                    "function": function_name,
                    "call_occurrences": occurrences,
                    "dry_run": self.dry_run,
                }
        return {"success": False, "error": f"Function '{function_name}' not found"}
