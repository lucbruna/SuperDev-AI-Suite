"""Safe dynamic-code execution guard (OWASP A03 / CWE-94, CWE-95).

The suite has a few places that execute generated or workflow-provided Python
code (workflow python nodes, coding evaluators). Raw ``exec`` with the full
builtins is an arbitrary code-execution hole. This module applies the same
AST-allowlist philosophy used by ``safe_condition_eval``:

* parse the code first and reject dangerous constructs before execution
  (imports, calls to non-allowlisted callables, underscore/dunder attribute
  access, hard-blocked builtins such as ``__import__``/``open``/``getattr``);
* run it with a restricted ``__builtins__`` namespace.
"""

from __future__ import annotations

import ast
import builtins as _builtins
from typing import Any

# Builtins that are safe to expose to generated code.
_DEFAULT_ALLOWED_BUILTINS = frozenset({
    "abs", "all", "any", "bool", "bytes", "chr", "complex", "dict", "divmod",
    "enumerate", "filter", "float", "format", "frozenset", "hash", "hex",
    "int", "isinstance", "issubclass", "iter", "len", "list", "map", "max",
    "min", "next", "oct", "ord", "pow", "print", "range", "repr", "reversed",
    "round", "set", "slice", "sorted", "str", "sum", "tuple", "zip",
    # Exceptions commonly needed by generated code.
    "ArithmeticError", "AssertionError", "AttributeError", "Exception",
    "IndexError", "KeyError", "LookupError", "RuntimeError", "StopIteration",
    "TypeError", "ValueError", "ZeroDivisionError",
})

# Names that are always blocked, even when added to an allowlist.
_HARD_BLOCKED = frozenset({
    "__import__", "eval", "exec", "compile", "open", "input", "breakpoint",
    "globals", "locals", "vars", "dir", "getattr", "setattr", "delattr",
    "exit", "quit", "help", "memoryview", "__build_class__", "super",
})

# Modules that workflow "imports" config may load.
_SAFE_IMPORT_MODULES = frozenset({
    "json", "math", "random", "datetime", "re", "collections", "statistics",
    "string", "itertools", "functools", "operator", "decimal", "fractions",
    "uuid", "base64", "hashlib", "copy", "typing", "enum", "dataclasses",
})


def _is_underscore_attr(name: str) -> bool:
    """Dunder/underscore attribute access is a classic sandbox escape."""
    return name.startswith("_")


def guard_code_exec(code: str,
                    extra_allowed: set[str] | None = None) -> ast.Module:
    """Parse *code* and raise ``ValueError`` on dangerous constructs.

    Blocks: imports, calls to non-allowlisted callables, underscore/dunder
    attribute access and hard-blocked builtin names.
    """
    allowed = set(_DEFAULT_ALLOWED_BUILTINS)
    if extra_allowed:
        allowed |= set(extra_allowed)

    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"invalid code: {exc}") from exc

    # Names defined by the code itself (defs/classes/assignments) are valid
    # call targets — collect them so the call allowlist doesn't reject them.
    defined = _collect_local_names(tree)

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ValueError("imports are not allowed in guarded code")
        if isinstance(node, ast.Attribute) and _is_underscore_attr(node.attr):
            raise ValueError(
                f"access to underscore attribute {node.attr!r} is blocked")
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                name = func.id
                if name in _HARD_BLOCKED:
                    raise ValueError(f"call to {name!r} is blocked")
                if name not in allowed and name not in defined:
                    raise ValueError(f"call to {name!r} is not allowed")
            elif isinstance(func, ast.Attribute):
                if _is_underscore_attr(func.attr):
                    raise ValueError(
                        f"call to underscore method {func.attr!r} is blocked")
            else:
                raise ValueError("unsupported call target")
    return tree


def _collect_local_names(tree: ast.Module) -> set[str]:
    """Collect names defined inside *tree* (functions, classes, assignments)."""
    defined: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined.add(target.id)
        elif (isinstance(node, ast.AnnAssign)
              and isinstance(node.target, ast.Name)):
            defined.add(node.target.id)
    return defined


def safe_builtins(extra_allowed: set[str] | None = None) -> dict[str, Any]:
    """Minimal builtins namespace for guarded execution."""
    names = set(_DEFAULT_ALLOWED_BUILTINS)
    if extra_allowed:
        names |= set(extra_allowed)
    names -= _HARD_BLOCKED
    return {name: getattr(_builtins, name) for name in names
            if hasattr(_builtins, name)}


def safe_exec(code: str,
              namespace: dict[str, Any] | None = None,
              extra_allowed: set[str] | None = None) -> dict[str, Any]:
    """Run *code* after the AST guard, with restricted builtins.

    Executes directly into *namespace* (mutating it, like ``exec``), so
    results written by *code* (e.g. ``result``) are visible to the caller.
    Returns the execution namespace.
    """
    tree = guard_code_exec(code, extra_allowed=extra_allowed)
    ns: dict[str, Any] = namespace if namespace is not None else {}
    ns.setdefault("__builtins__", safe_builtins(extra_allowed))
    exec(compile(tree, "<guarded-exec>", "exec"), ns)  # guarded by AST check
    return ns


def validate_import_statement(stmt: str) -> str:
    """Validate an import statement against the safe-module allowlist."""
    try:
        tree = ast.parse(stmt, mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"invalid import statement: {exc}") from exc

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found = True
            for alias in node.names:
                if alias.name.split(".")[0] not in _SAFE_IMPORT_MODULES:
                    raise ValueError(
                        f"import of module {alias.name!r} is not allowed")
        elif isinstance(node, ast.ImportFrom):
            found = True
            root = (node.module or "").split(".")[0]
            if root not in _SAFE_IMPORT_MODULES:
                raise ValueError(
                    f"import from module {node.module!r} is not allowed")
        elif not isinstance(node, (ast.Module, ast.Expr, ast.Import,
                                   ast.ImportFrom, ast.Name, ast.alias)):
            raise ValueError(
                f"unsupported statement in import: {type(node).__name__}")
    if not found:
        raise ValueError("no import statement found")
    return stmt
