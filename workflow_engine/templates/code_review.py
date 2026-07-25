from __future__ import annotations

from typing import Any


def code_review_template() -> dict[str, Any]:
    return {
        "metadata": {
            "name": "Code Review Pipeline",
            "description": "Checkout code, lint, run tests, review, and report",
        },
        "nodes": [
            {
                "id": "checkout",
                "type": "TOOL",
                "name": "Checkout Code",
                "config": {"tool_name": "git_checkout", "params": {"repo": "$repo_url", "branch": "$branch"}},
            },
            {
                "id": "lint",
                "type": "SHELL",
                "name": "Run Linter",
                "config": {"command": "ruff check .", "timeout": 120},
            },
            {
                "id": "test",
                "type": "SHELL",
                "name": "Run Tests",
                "config": {"command": "pytest tests/", "timeout": 300},
            },
            {
                "id": "review",
                "type": "AGENT",
                "name": "Code Review Agent",
                "config": {"agent_name": "reviewer", "task": "Review the code changes", "model": "gpt-4"},
            },
            {
                "id": "report",
                "type": "TOOL",
                "name": "Generate Report",
                "config": {"tool_name": "report_generator", "params": {"format": "markdown"}},
            },
        ],
        "edges": [
            {"source": "checkout", "target": "lint"},
            {"source": "lint", "target": "test"},
            {"source": "test", "target": "review"},
            {"source": "review", "target": "report"},
        ],
    }
