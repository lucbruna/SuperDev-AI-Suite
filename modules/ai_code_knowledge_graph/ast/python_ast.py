"""Python AST extraction — normalized entities from the stdlib ``ast``.

Converts Python source into the module's canonical entity list (file,
imports, classes, methods, functions) using only the standard library.
Syntax errors surface as ``{"error": {...}}`` without raising.
"""
from __future__ import annotations

import ast
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import (
    class_entity,
    file_entity,
    function_entity,
    import_entity,
    method_entity,
)


def extract(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse Python source and return ``{language, rel_path, entities, error}``."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError) as exc:
        error: dict[str, Any] = {"message": str(exc)}
        if isinstance(exc, SyntaxError) and exc.lineno:
            error["line"] = exc.lineno
        return {"language": "python", "rel_path": rel_path, "entities": [], "error": error}

    line_count = len(text.splitlines())
    entities: list[dict[str, Any]] = [file_entity(rel_path or "<string>", line_count)]

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            entities.extend(_imports(node))
        elif isinstance(node, ast.ClassDef):
            entities.append(_class(node, rel_path))
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    entities.extend(_imports(child))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entities.append(_function(node, rel_path))

    return {"language": "python", "rel_path": rel_path, "entities": entities, "error": None}


# ── entity builders ──────────────────────────────────────────────────────────

def _imports(node: ast.Import | ast.ImportFrom) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            out.append(import_entity(alias.name, alias=alias.asname, line=node.lineno))
        return out
    module = node.module or ""
    for alias in node.names:
        if alias.name == "*":
            out.append(import_entity("*", source=module, line=node.lineno))
        else:
            out.append(import_entity(alias.name, source=module, alias=alias.asname, line=node.lineno))
    return out


def _class(node: ast.ClassDef, rel_path: str) -> dict[str, Any]:
    methods = [_method(child) for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))]
    bases = [_full_name(base) for base in node.bases]
    decorators = [_decorator_name(decorator) for decorator in node.decorator_list]
    end = getattr(node, "end_lineno", None) or node.lineno
    return class_entity(
        node.name,
        node.lineno,
        end,
        bases=[name for name in bases if name],
        decorators=[name for name in decorators if name],
        methods=methods,
        module=rel_path or None,
    )


def _method(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    decorators = [_decorator_name(decorator) for decorator in node.decorator_list]
    end = getattr(node, "end_lineno", None) or node.lineno
    return method_entity(
        node.name,
        node.lineno,
        end,
        params=_arg_names(node.args),
        decorators=[name for name in decorators if name],
        static="staticmethod" in decorators,
        classmethod="classmethod" in decorators,
        async_=isinstance(node, ast.AsyncFunctionDef),
    )


def _function(node: ast.FunctionDef | ast.AsyncFunctionDef, rel_path: str) -> dict[str, Any]:
    decorators = [_decorator_name(decorator) for decorator in node.decorator_list]
    end = getattr(node, "end_lineno", None) or node.lineno
    return function_entity(
        node.name,
        node.lineno,
        end,
        params=_arg_names(node.args),
        decorators=[name for name in decorators if name],
        async_=isinstance(node, ast.AsyncFunctionDef),
        module=rel_path or None,
    )


# ── small helpers ────────────────────────────────────────────────────────────

def _full_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _full_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Subscript):
        return _full_name(node.value)
    return None


def _decorator_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        return _full_name(node.func)
    return _full_name(node)


def _arg_names(args: ast.arguments) -> list[str]:
    names = [argument.arg for argument in args.args]
    if args.vararg is not None:
        names.append(f"*{args.vararg.arg}")
    if args.kwarg is not None:
        names.append(f"**{args.kwarg.arg}")
    names.extend(argument.arg for argument in args.kwonlyargs)
    return names
