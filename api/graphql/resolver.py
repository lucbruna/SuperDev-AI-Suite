from __future__ import annotations

from typing import Any, Callable


class Resolver:
    """Base class for GraphQL resolvers."""

    async def resolve(self, parent: Any, args: dict[str, Any], context: Any) -> Any:
        raise NotImplementedError


class ResolverRegistry:
    """Maps GraphQL type.field -> resolver function."""

    def __init__(self) -> None:
        self._resolvers: dict[str, Callable] = {}

    def register(self, type_name: str, field_name: str, resolver: Callable) -> None:
        key = f"{type_name}.{field_name}"
        self._resolvers[key] = resolver

    def get(self, type_name: str, field_name: str) -> Callable | None:
        return self._resolvers.get(f"{type_name}.{field_name}")

    def has_resolver(self, type_name: str, field_name: str) -> bool:
        return f"{type_name}.{field_name}" in self._resolvers

    def resolve_field(self, type_name: str, field_name: str, parent: Any, args: dict[str, Any], context: Any) -> Any:
        resolver = self.get(type_name, field_name)
        if resolver is None:
            if isinstance(parent, dict):
                return parent.get(field_name)
            return getattr(parent, field_name, None)
        result = resolver(parent, args, context)
        if hasattr(result, "__await__"):
            import asyncio
            return asyncio.ensure_future(result)
        return result

    def to_dict(self) -> dict[str, Any]:
        return {"resolvers": list(self._resolvers.keys()), "count": len(self._resolvers)}
