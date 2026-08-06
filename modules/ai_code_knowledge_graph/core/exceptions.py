"""Exception hierarchy for the AI Code Knowledge Graph.

Every exception carries a structured error_code and optional context dict so
API handlers can serialize them into consistent JSON responses (mirrors the
exception conventions used across the suite).
"""
from __future__ import annotations

from typing import Any


class KnowledgeError(Exception):
    """Base exception for the whole knowledge graph module."""

    error_code: str = "KNOWLEDGE_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str = "An unexpected knowledge graph error occurred",
        *,
        context: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        self.message = message
        self.context = context or {}
        self.cause = cause
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.context:
            result["context"] = self.context
        return result


class ScanError(KnowledgeError):
    error_code = "KNOWLEDGE_SCAN_ERROR"
    status_code = 500


class ParseError(KnowledgeError):
    error_code = "KNOWLEDGE_PARSE_ERROR"
    status_code = 500


class GraphBuildError(KnowledgeError):
    error_code = "KNOWLEDGE_GRAPH_BUILD_ERROR"
    status_code = 500


class StoreError(KnowledgeError):
    error_code = "KNOWLEDGE_STORE_ERROR"
    status_code = 500


class NotFoundError(KnowledgeError):
    error_code = "KNOWLEDGE_NOT_FOUND"
    status_code = 404

    def __init__(self, resource: str, resource_id: str, **kw: Any):
        super().__init__(
            f"{resource} with id '{resource_id}' not found",
            context={"resource": resource, "id": resource_id},
            **kw,
        )


class PermissionDeniedError(KnowledgeError):
    error_code = "KNOWLEDGE_FORBIDDEN"
    status_code = 403
