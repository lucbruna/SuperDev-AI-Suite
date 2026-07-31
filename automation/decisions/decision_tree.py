"""Evaluates decision trees against input data."""

from __future__ import annotations

from typing import Any

from automation.decisions.decision_models import (DecisionBranch,
                                                  DecisionNode,
                                                  DecisionResult)
from automation.triggers.trigger_evaluator import TriggerEvaluator


class DecisionTree:
    """A tree of questions whose branches lead to actions."""

    def __init__(self, tree_id: str, name: str, root_id: str,
                 nodes: dict[str, DecisionNode],
                 evaluator: TriggerEvaluator | None = None) -> None:
        self.tree_id = tree_id
        self.name = name
        self.root_id = root_id
        self.nodes = nodes
        self.evaluator = evaluator or TriggerEvaluator()

    def decide(self, data: dict[str, Any]) -> DecisionResult:
        current = self.root_id
        path: list[str] = []
        guard = 0
        while current in self.nodes:
            node = self.nodes[current]
            path.append(node.node_id)
            if node.action is not None:
                return DecisionResult(self.tree_id, node.action, path,
                                      node.action, dict(node.params))
            matched: DecisionBranch | None = None
            for branch in node.branches:
                if self.evaluator.evaluate_condition(branch.condition, data):
                    matched = branch
                    break
            if matched is None:
                return DecisionResult(self.tree_id, "no_branch_matched",
                                      path, None, {})
            current = matched.target
            guard += 1
            if guard > 100:
                return DecisionResult(self.tree_id, "max_depth_exceeded",
                                      path, None, {})
        return DecisionResult(self.tree_id, "unknown_node", path, None, {})
