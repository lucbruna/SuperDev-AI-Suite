from __future__ import annotations

import ast
import operator
from typing import Any

_SAFE_OPERATORS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
    ast.Not: operator.not_,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_BLOCKED = frozenset(
    {
        "__import__",
        "exec",
        "eval",
        "compile",
        "open",
        "getattr",
        "setattr",
        "delattr",
        "globals",
        "locals",
        "vars",
        "dir",
        "type",
        "super",
        "breakpoint",
        "exit",
        "quit",
        "help",
        "input",
        "print",
    }
)


def _safe_eval(node: ast.AST, context: dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, context)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in _BLOCKED:
            raise ValueError(f"Access to '{node.id}' is blocked")
        if node.id in context:
            return context[node.id]
        if node.id in ("True", "False", "None"):
            return {"True": True, "False": False, "None": None}[node.id]
        raise NameError(f"'{node.id}' not defined")
    if isinstance(node, ast.BinOp):
        op = _SAFE_OPERATORS.get(type(node.op))
        if not op:
            raise ValueError(f"Operator {type(node.op).__name__} not allowed")
        return op(_safe_eval(node.left, context), _safe_eval(node.right, context))
    if isinstance(node, ast.UnaryOp):
        op = _SAFE_OPERATORS.get(type(node.op))
        if not op:
            raise ValueError(f"Operator {type(node.op).__name__} not allowed")
        return op(_safe_eval(node.operand, context))
    if isinstance(node, ast.BoolOp):
        values = [_safe_eval(v, context) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
    if isinstance(node, ast.Compare):
        left = _safe_eval(node.left, context)
        for op, comparator in zip(node.ops, node.comparators, strict=False):
            op_fn = _SAFE_OPERATORS.get(type(op))
            if not op_fn:
                raise ValueError(f"Comparison {type(op).__name__} not allowed")
            right = _safe_eval(comparator, context)
            if not op_fn(left, right):
                return False
            left = right
        return True
    if isinstance(node, ast.Call):
        raise ValueError("Function calls not allowed")
    if isinstance(node, ast.Attribute):
        raise ValueError("Attribute access not allowed")
    raise ValueError(f"Unsupported expression: {type(node).__name__}")


def safe_condition_eval(expression: str, context: dict[str, Any]) -> bool:
    tree = ast.parse(expression, mode="eval")
    return bool(_safe_eval(tree, context))
