"""API builder skill — REST API design blueprint."""
from __future__ import annotations
from typing import Any


class ApiBuilderSkill:
    """Design a REST API: resources, endpoints, and conventions."""

    skill_id = "api_builder"
    skill_name = "API Builder"
    skill_version = "1.0.0"
    skill_description = "REST API blueprint with resources, methods, and conventions."
    skill_category = "development"
    skill_tags = ["development", "api", "rest", "backend"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        resource: str,
        *,
        version: str = "v1",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return an API design for a resource."""
        base = f"/api/{version}/{resource}"
        return {
            "resource": resource,
            "base_path": base,
            "language": language,
            "endpoints": [
                {"method": "GET", "path": base, "purpose": "list with pagination"},
                {"method": "POST", "path": base, "purpose": "create"},
                {"method": "GET", "path": f"{base}/{{id}}", "purpose": "retrieve one"},
                {"method": "PATCH", "path": f"{base}/{{id}}", "purpose": "partial update"},
                {"method": "DELETE", "path": f"{base}/{{id}}", "purpose": "delete"},
            ],
            "conventions": {
                "errors": "RFC 7807 problem+json",
                "pagination": "cursor-based",
                "auth": "bearer token",
                "idempotency": "POST accepts Idempotency-Key",
            },
            "schema": {"id": "uuid", "created_at": "iso8601", "updated_at": "iso8601"},
        }
