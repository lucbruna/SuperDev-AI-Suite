from __future__ import annotations

from typing import Any, Callable


class GraphQLScalar:
    """Represents a GraphQL scalar type."""

    def __init__(self, name: str, coerce: Callable[[Any], Any] | None = None) -> None:
        self.name = name
        self._coerce = coerce or (lambda v: v)

    def coerce(self, value: Any) -> Any:
        return self._coerce(value)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "SCALAR", "name": self.name}


GRAPHQL_STRING = GraphQLScalar("String", str)
GRAPHQL_INT = GraphQLScalar("Int", int)
GRAPHQL_FLOAT = GraphQLScalar("Float", float)
GRAPHQL_BOOLEAN = GraphQLScalar("Boolean", bool)
GRAPHQL_ID = GraphQLScalar("ID", str)

BUILTIN_SCALARS: dict[str, GraphQLScalar] = {
    "String": GRAPHQL_STRING,
    "Int": GRAPHQL_INT,
    "Float": GRAPHQL_FLOAT,
    "Boolean": GRAPHQL_BOOLEAN,
    "ID": GRAPHQL_ID,
}


class GraphQLNonNull:
    """Wraps a type as non-nullable."""

    def __init__(self, of_type: Any) -> None:
        self.of_type = of_type

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "NON_NULL", "ofType": self.of_type.to_dict() if hasattr(self.of_type, "to_dict") else self.of_type}


class GraphQLList:
    """Wraps a type as a list."""

    def __init__(self, of_type: Any) -> None:
        self.of_type = of_type

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "LIST", "ofType": self.of_type.to_dict() if hasattr(self.of_type, "to_dict") else self.of_type}


class GraphQLField:
    """Represents a field on a GraphQL type."""

    def __init__(
        self,
        name: str,
        field_type: Any,
        resolver: Callable | None = None,
        args: dict[str, Any] | None = None,
        description: str = "",
    ) -> None:
        self.name = name
        self.field_type = field_type
        self.resolver = resolver
        self.args = args or {}
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.field_type.to_dict() if hasattr(self.field_type, "to_dict") else str(self.field_type),
            "description": self.description,
            "args": {k: v.to_dict() if hasattr(v, "to_dict") else str(v) for k, v in self.args.items()},
        }


class GraphQLType:
    """Represents a GraphQL object type."""

    def __init__(self, name: str, fields: dict[str, GraphQLField], description: str = "") -> None:
        self.name = name
        self.fields = fields
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "OBJECT",
            "name": self.name,
            "description": self.description,
            "fields": {n: f.to_dict() for n, f in self.fields.items()},
        }


class GraphQLEnum:
    """Represents a GraphQL enum type."""

    def __init__(self, name: str, values: dict[str, str]) -> None:
        self.name = name
        self.values = values

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ENUM",
            "name": self.name,
            "values": [{"name": k, "description": v} for k, v in self.values.items()],
        }


class GraphQLInputType:
    """Represents a GraphQL input object type."""

    def __init__(self, name: str, fields: dict[str, Any], description: str = "") -> None:
        self.name = name
        self.fields = fields
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "INPUT_OBJECT",
            "name": self.name,
            "description": self.description,
            "fields": {n: f.to_dict() if hasattr(f, "to_dict") else str(f) for n, f in self.fields.items()},
        }


def build_schema(
    types: dict[str, Any],
    query_type: str = "Query",
    mutation_type: str | None = None,
) -> dict[str, Any]:
    """Build an introspection-ready schema definition."""
    all_types: dict[str, Any] = dict(BUILTIN_SCALARS)
    cast_types: dict[str, Any] = {k: v for k, v in types.items()}
    all_types.update(cast_types)
    schema: dict[str, Any] = {
        "queryType": {"name": query_type},
        "types": [t.to_dict() for t in all_types.values()],
    }
    if mutation_type and mutation_type in types:
        schema["mutationType"] = {"name": mutation_type}
    return schema
