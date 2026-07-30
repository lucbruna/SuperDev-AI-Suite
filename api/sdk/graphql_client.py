from __future__ import annotations

from typing import Any

from .client import BaseClient


class GraphQLClient(BaseClient):
    """GraphQL client with query, mutation, and subscription support."""

    def query(self, query: str, variables: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        body: dict[str, Any] = {"query": query}
        if variables:
            body["variables"] = variables
        return self.request("POST", "/graphql", body=body, **kwargs)

    def mutate(self, mutation: str, variables: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        body: dict[str, Any] = {"query": mutation}
        if variables:
            body["variables"] = variables
        return self.request("POST", "/graphql", body=body, **kwargs)

    def subscribe(self, subscription: str, variables: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        body: dict[str, Any] = {"query": subscription}
        if variables:
            body["variables"] = variables
        return self.request("POST", "/graphql", body=body, **kwargs)

    def introspect(self) -> Any:
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types { name kind description fields { name type { name kind } } }
                queryType { name }
                mutationType { name }
                subscriptionType { name }
            }
        }
        """
        return self.query(introspection_query)
