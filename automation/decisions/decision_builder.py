"""Fluent builder for decision trees."""

from __future__ import annotations

from typing import Any

from automation.decisions.decision_models import (DecisionBranch,
                                                  DecisionNode)
from automation.decisions.decision_tree import DecisionTree


class DecisionBuilder:
    """Builds DecisionTree instances step by step."""

    def __init__(self) -> None:
        self._tree_id = ""
        self._name = ""
        self._nodes: dict[str, DecisionNode] = {}
        self._root: str | None = None

    def id(self, tree_id: str) -> "DecisionBuilder":
        self._tree_id = tree_id
        return self

    def name(self, name: str) -> "DecisionBuilder":
        self._name = name
        return self

    def node(self, node_id: str, question: str = "") -> "DecisionBuilder":
        self._nodes[node_id] = DecisionNode(node_id, question)
        return self

    def leaf(self, node_id: str, action: str,
             params: dict[str, Any] | None = None) -> "DecisionBuilder":
        self._nodes[node_id] = DecisionNode(node_id, action=action,
                                            params=params or {})
        return self

    def branch(self, node_id: str, branch_id: str,
               condition: dict[str, Any], to: str) -> "DecisionBuilder":
        self._nodes[node_id].branches.append(
            DecisionBranch(branch_id, condition, to))
        return self

    def root(self, node_id: str) -> "DecisionBuilder":
        self._root = node_id
        return self

    def build(self) -> DecisionTree:
        root = self._root or next(iter(self._nodes), None) or ""
        return DecisionTree(self._tree_id, self._name, root,
                            dict(self._nodes))
