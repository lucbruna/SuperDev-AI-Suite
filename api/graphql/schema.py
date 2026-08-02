from __future__ import annotations

from typing import Any

from ..api_logger import APILogger
from .resolver import ResolverRegistry
from .types import (
    BUILTIN_SCALARS,
    GraphQLEnum,
    GraphQLField,
    GraphQLInputType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLScalar,
    GraphQLType,
    build_schema,
)


class GraphQLSchema:
    """GraphQL schema with type registry and query execution."""

    def __init__(self, logger: APILogger | None = None) -> None:
        self._types: dict[str, Any] = {}
        self._query_type: str = "Query"
        self._mutation_type: str | None = None
        self.resolvers = ResolverRegistry()
        self._logger = logger or APILogger("graphql.schema")

    def register_type(self, graphql_type: GraphQLType | GraphQLEnum | GraphQLInputType | GraphQLScalar) -> None:
        self._types[graphql_type.name] = graphql_type

    def add_type(self, name: str, fields: dict[str, Any]) -> None:
        field_defs = {k: GraphQLField(k, v) for k, v in fields.items()}
        self._types[name] = GraphQLType(name=name, fields=field_defs)

    def get_types(self) -> dict[str, Any]:
        return dict(self._types)

    def set_query_type(self, name: str) -> None:
        self._query_type = name

    def set_mutation_type(self, name: str) -> None:
        self._mutation_type = name

    def get_type(self, name: str) -> Any:
        return self._types.get(name) or BUILTIN_SCALARS.get(name)

    def get_field_value(self, field_type: Any, value: Any) -> Any:
        if isinstance(field_type, GraphQLNonNull):
            if value is None:
                raise ValueError("Non-null field returned null")
            return self.get_field_value(field_type.of_type, value)
        if value is None:
            return None
        if isinstance(field_type, GraphQLList):
            if not isinstance(value, (list, tuple)):
                value = [value]
            return [self.get_field_value(field_type.of_type, v) for v in value]
        if isinstance(field_type, GraphQLScalar):
            return field_type.coerce(value)
        return value

    async def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        context: Any = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query (simplified parser)."""
        import json
        query = query.strip()
        variables = variables or {}
        context = context or {}

        operation_type = "query"
        operation_name = ""

        if query.startswith("mutation"):
            operation_type = "mutation"
            query = query[len("mutation"):].strip()
        elif query.startswith("query"):
            query = query[len("query"):].strip()

        selection_set = self._parse_selection_set(query)
        if not selection_set:
            return {"errors": [{"message": "No selection set found"}]}

        type_name: str = (self._mutation_type if operation_type == "mutation" else self._query_type) or self._query_type
        graphql_type = self.get_type(type_name)
        if graphql_type is None:
            return {"errors": [{"message": f"Unknown type: {type_name}"}]}

        result = await self._execute_fields(graphql_type, selection_set, None, context)
        return {"data": result}

    def _parse_selection_set(self, query: str) -> list[dict[str, Any]]:
        """Simple brace-based selection set parser."""
        fields: list[dict[str, Any]] = []
        brace_depth = 0
        current_field = ""
        in_field = False
        sub_fields: list[str] = []

        for char in query:
            if char == "{":
                if brace_depth == 0 and in_field:
                    sub_fields = []
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth == 0 and in_field:
                    fields.append({"name": current_field.strip(), "fields": self._parse_field_list(sub_fields)})
                    current_field = ""
                    in_field = False
                    sub_fields = []
            elif brace_depth == 1:
                if char == " " and not in_field:
                    continue
                if brace_depth > 0:
                    sub_fields.append(char)

        if current_field.strip():
            fields.append({"name": current_field.strip(), "fields": []})
        return fields

    def _parse_field_list(self, chars: list[str]) -> list[dict[str, Any]]:
        raw = "".join(chars).strip()
        if not raw:
            return []
        names = [n.strip() for n in raw.replace("\n", " ").split() if n.strip()]
        return [{"name": n, "fields": []} for n in names]

    async def _execute_fields(
        self,
        graphql_type: Any,
        fields: list[dict[str, Any]],
        parent: Any,
        context: Any,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if not hasattr(graphql_type, "fields"):
            return {}

        field_defs = graphql_type.fields
        for field_spec in fields:
            field_name = field_spec["name"]
            field_def = field_defs.get(field_name)
            if field_def is None:
                continue

            args = {}
            raw_value = self.resolvers.resolve_field(graphql_type.name, field_name, parent, args, context)
            if hasattr(raw_value, "__await__"):
                import asyncio
                raw_value = await raw_value

            value = self.get_field_value(field_def.field_type, raw_value)

            if field_spec["fields"] and isinstance(value, (dict, list)):
                if isinstance(value, list):
                    value = [await self._execute_fields(field_def.field_type.of_type if hasattr(field_def.field_type, "of_type") else graphql_type, field_spec["fields"], v, context) for v in value]
                else:
                    child_type = self.get_type(field_def.field_type.name if hasattr(field_def.field_type, "name") else "")
                    if child_type and hasattr(child_type, "fields"):
                        value = await self._execute_fields(child_type, field_spec["fields"], value, context)

            result[field_name] = value
        return result

    def introspection(self) -> dict[str, Any]:
        return build_schema(self._types, self._query_type, self._mutation_type)

    def to_dict(self) -> dict[str, Any]:
        return {
            "types": list(self._types.keys()),
            "query_type": self._query_type,
            "mutation_type": self._mutation_type,
            "resolvers": self.resolvers.to_dict(),
        }
