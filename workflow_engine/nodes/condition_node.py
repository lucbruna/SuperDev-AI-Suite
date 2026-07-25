from __future__ import annotations

import ast
import operator
from typing import Any

from workflow_engine.graph.node import NodeType
from workflow_engine.nodes.base_node import BaseNode, NodeResult

# Safe operators for expression evaluation
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

# Block dangerous builtins
_BLOCKED_BUILTINS = frozenset({
    "__import__", "exec", "eval", "compile", "open", "getattr", "setattr",
    "delattr", "globals", "locals", "vars", "dir", "type", "super",
    "breakpoint", "exit", "quit", "help", "input", "print",
})


def _safe_eval_node(node: ast.AST, context: dict[str, Any]) -> Any:
    """Recursively evaluate an AST node safely without using eval()."""
    if isinstance(node, ast.Expression):
        return _safe_eval_node(node.body, context)

    if isinstance(node, ast.Constant):
        return node.value

    if isinstance(node, ast.Name):
        if node.id in _BLOCKED_BUILTINS:
            raise ValueError(f"Access to '{node.id}' is blocked")
        if node.id in context:
            return context[node.id]
        if node.id in ("True", "False", "None"):
            return {"True": True, "False": False, "None": None}[node.id]
        raise NameError(f"Name '{node.id}' is not defined in context")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Binary operator {op_type.__name__} is not allowed")
        left = _safe_eval_node(node.left, context)
        right = _safe_eval_node(node.right, context)
        return _SAFE_OPERATORS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unary operator {op_type.__name__} is not allowed")
        operand = _safe_eval_node(node.operand, context)
        return _SAFE_OPERATORS[op_type](operand)

    if isinstance(node, ast.BoolOp):
        op_type = type(node.op)
        values = [_safe_eval_node(v, context) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        elif isinstance(node.op, ast.Or):
            return any(values)

    if isinstance(node, ast.Compare):
        left = _safe_eval_node(node.left, context)
        for op, comparator in zip(node.ops, node.comparators, strict=False):
            op_type = type(op)
            if op_type not in _SAFE_OPERATORS:
                raise ValueError(f"Comparison operator {op_type.__name__} is not allowed")
            right = _safe_eval_node(comparator, context)
            result = _SAFE_OPERATORS[op_type](left, right)
            if not result:
                return False
            left = right
        return True

    if isinstance(node, ast.Call):
        raise ValueError("Function calls are not allowed in conditions")

    if isinstance(node, ast.Attribute):
        raise ValueError("Attribute access is not allowed in conditions")

    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
        raise ValueError("Collection literals are not allowed in conditions")

    raise ValueError(f"Unsupported expression type: {type(node).__name__}")


def safe_condition_eval(expression: str, context: dict[str, Any]) -> bool:
    """Safely evaluate a boolean expression against a context dictionary.

    Supports: comparisons (==, !=, <, >, <=, >=), boolean operators (and, or, not),
    arithmetic (+, -, *, /, //, %, **), name lookups from context, and constants.

    Blocks: function calls, attribute access, imports, assignments, collections.
    """
    tree = ast.parse(expression, mode="eval")
    result = _safe_eval_node(tree, context)
    return bool(result)


class ConditionNode(BaseNode):
    node_type: NodeType = NodeType.CONDITION

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        expression = self.config.get("expression", "")
        if not expression:
            return NodeResult(
                node_id=self.config.get("node_id", ""),
                status="failed",
                error="No expression provided",
            )
        try:
            result = safe_condition_eval(expression, context)
        except Exception as e:
            return NodeResult(
                node_id=self.config.get("node_id", ""),
                status="failed",
                error=f"Condition evaluation error: {e}",
            )
        return NodeResult(
            node_id=self.config.get("node_id", ""),
            status="success",
            output={"condition_result": result, "expression": expression},
        )
