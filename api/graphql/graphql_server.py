from __future__ import annotations

import json
from typing import Any

from ..api_logger import APILogger
from ..api_metrics import APIMetrics
from ..api_models import APIRequest, APIResponse
from .mutations import MutationRegistry
from .schema import GraphQLSchema
from .subscriptions import SubscriptionManager
from .types import GraphQLType, build_schema


class GraphQLServer:
    """GraphQL server handling query/mutation execution."""

    def __init__(
        self,
        schema: GraphQLSchema | None = None,
        logger: APILogger | None = None,
        metrics: APIMetrics | None = None,
    ) -> None:
        self.schema = schema or GraphQLSchema(logger=logger)
        self.mutations = MutationRegistry()
        self.subscriptions = SubscriptionManager()
        self._logger = logger or APILogger("graphql.server")
        self._metrics = metrics

    async def execute(self, request: APIRequest) -> APIResponse:
        body = request.body if isinstance(request.body, dict) else {}
        query = body.get("query", "")
        variables = body.get("variables", {})

        if not query:
            return APIResponse(
                status_code=400,
                body=json.dumps({"errors": [{"message": "No query provided"}]}),
                headers={"content-type": "application/json"},
                request_id=request.request_id,
            )

        try:
            result = await self.schema.execute(query, variables, request)
            body_str = json.dumps(result, default=str, ensure_ascii=False)
            return APIResponse(
                status_code=200,
                body=body_str,
                headers={"content-type": "application/json"},
                request_id=request.request_id,
            )
        except Exception as e:
            self._logger.error("GraphQL execution error", error=str(e))
            return APIResponse(
                status_code=500,
                body=json.dumps({"errors": [{"message": "Internal server error"}]}),
                headers={"content-type": "application/json"},
                request_id=request.request_id,
            )

    def add_type(self, graphql_type: GraphQLType) -> None:
        self.schema.register_type(graphql_type)

    def introspection(self) -> dict[str, Any]:
        return self.schema.introspection()

    def to_dict(self) -> dict[str, Any]:
        return {
            "subsystem": "graphql",
            "schema": self.schema.to_dict(),
            "mutations": self.mutations.to_dict(),
            "subscriptions": self.subscriptions.to_dict(),
        }
