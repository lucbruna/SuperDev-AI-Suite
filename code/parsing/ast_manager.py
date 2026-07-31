from __future__ import annotations

import ast
import logging
from typing import Any


class ASTManager:
    """Manages Abstract Syntax Tree operations.

    ``parse`` turns Python source code into a structured index of its
    imports, classes and functions using :func:`ast.parse`, and ``to_dict``
    serializes any AST node into a JSON-friendly structure.
    """

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.parsing.ast")

    def parse(self, code: str) -> dict[str, Any] | None:
        """Parse *code* and extract imports, classes and functions.

        Returns a dict with the keys ``imports`` (list of
        ``{"module", "names", "asname", "level"}``), ``classes`` and
        ``functions`` (lists of names) and ``ast`` (the root tree), or
        ``None`` when the source has a syntax error.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            self._log.warning("Syntax error while parsing code: %s", exc)
            return None

        imports: list[dict[str, Any]] = []
        classes: list[str] = []
        functions: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({"module": alias.name,
                                    "names": [],
                                    "asname": alias.asname,
                                    "level": 0})
            elif isinstance(node, ast.ImportFrom):
                # ``from . import X`` has module=None; the name lives in
                # node.names[0].name.
                module = node.module or (node.names[0].name if node.names
                                         else "")
                imports.append({"module": module,
                                "names": [a.name for a in node.names],
                                "asname": None,
                                "level": node.level})
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)

        return {"imports": imports,
                "classes": classes,
                "functions": functions,
                "ast": tree}

    def to_dict(self, node: Any) -> dict[str, Any]:
        """Serialize an AST node (or plain value) to a JSON-friendly dict."""
        if isinstance(node, ast.AST):
            fields = {field: self.to_dict(getattr(node, field))
                      for field in node._fields}
            return {"type": type(node).__name__, **fields}
        if isinstance(node, list):
            return [self.to_dict(item) for item in node]
        if isinstance(node, (str, int, float, bool)) or node is None:
            return node
        return repr(node)
