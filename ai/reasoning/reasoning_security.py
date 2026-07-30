from __future__ import annotations

from typing import Any


class ReasoningSecurity:
    """Security checks for reasoning operations."""

    @staticmethod
    def validate_input(query: str) -> dict[str, Any]:
        errors: list[str] = []
        if not query or not query.strip():
            errors.append("Query is empty")
        if len(query) > 100_000:
            errors.append("Query exceeds maximum length")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def sanitize_output(decision: str) -> str:
        return decision.strip()

    @staticmethod
    def check_permission(user_role: str, action: str) -> bool:
        allowed_actions: dict[str, list[str]] = {
            "admin": ["reason", "evaluate", "validate", "configure"],
            "user": ["reason", "evaluate"],
            "viewer": ["evaluate"],
        }
        return action in allowed_actions.get(user_role, [])
