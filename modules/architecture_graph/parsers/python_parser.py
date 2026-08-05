"""Python source parser (AST based).

Extracts imports, classes, functions, router definitions and route
decorators so the scanner can build file->file and file->api edges.
"""
from __future__ import annotations

import ast
import re
from typing import Any

_ROUTE_DECORATOR_RE = re.compile(
    r"@(?P<var>[A-Za-z_][\w]*)\.(?P<method>get|post|put|patch|delete|head|options)"
    r"\s*\(\s*(?P<quote>['\"])(?P<path>.*?)(?P=quote)"
)


def _parse_route_decorators(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for decorator in node.decorator_list:
        text = ast.unparse(decorator) if hasattr(ast, "unparse") else ""
        match = _ROUTE_DECORATOR_RE.search(text)
        if match:
            routes.append(
                {
                    "variable": match.group("var"),
                    "method": match.group("method"),
                    "path": match.group("path"),
                    "line": node.lineno,
                }
            )
    return routes


def parse(text: str, path: str = "") -> dict[str, Any]:
    """Parse a Python source file into a structured summary."""
    result: dict[str, Any] = {
        "imports": [],
        "classes": [],
        "functions": [],
        "route_decorators": [],
        "router_defined": False,
        "error": None,
    }
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        result["error"] = f"SyntaxError: {exc}"
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(
                    {"module": alias.name, "name": alias.asname or alias.name, "line": node.lineno}
                )
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                result["imports"].append(
                    {
                        "module": (node.module or ""),
                        "name": alias.name,
                        "line": node.lineno,
                        "level": node.level,
                    }
                )
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append({"name": node.name, "line": node.lineno})
            result["route_decorators"].extend(_parse_route_decorators(node))

    result["router_defined"] = "APIRouter(" in text or "FastAPI(" in text
    return result
