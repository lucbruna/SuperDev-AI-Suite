"""Validation for decision trees."""

from __future__ import annotations

from typing import Any


class DecisionValidator:
    """Checks decision trees for structural errors."""

    def validate(self, tree: Any) -> list[str]:
        issues: list[str] = []
        if not tree.tree_id:
            issues.append("tree_id is required")
        if not tree.name:
            issues.append("name is required")
        if not tree.nodes:
            issues.append("tree has no nodes")
            return issues
        if tree.root_id not in tree.nodes:
            issues.append(f"root node '{tree.root_id}' not found")

        for node_id, node in tree.nodes.items():
            for branch in node.branches:
                if branch.target not in tree.nodes:
                    issues.append(
                        f"branch '{branch.branch_id}' of node '{node_id}' "
                        f"targets unknown node '{branch.target}'")
        return issues
