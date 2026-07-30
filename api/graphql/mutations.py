from __future__ import annotations

from typing import Any, Callable


class MutationRegistry:
    """Registry for GraphQL mutations."""

    def __init__(self) -> None:
        self._mutations: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        resolver: Callable,
        args: dict[str, Any] | None = None,
        description: str = "",
    ) -> None:
        self._mutations[name] = {
            "name": name,
            "resolver": resolver,
            "args": args or {},
            "description": description,
        }

    def get(self, name: str) -> dict[str, Any] | None:
        return self._mutations.get(name)

    async def execute(self, name: str, args: dict[str, Any], context: Any) -> dict[str, Any]:
        mutation = self._mutations.get(name)
        if mutation is None:
            return {"errors": [{"message": f"Unknown mutation: {name}"}]}
        try:
            result = mutation["resolver"](None, args, context)
            if hasattr(result, "__await__"):
                result = await result
            return {"data": {name: result}} if result is not None else {"data": {name: None}}
        except Exception as e:
            return {"errors": [{"message": str(e)}]}

    def list_mutations(self) -> list[dict[str, Any]]:
        return [
            {"name": m["name"], "description": m["description"], "args": list(m["args"].keys())}
            for m in self._mutations.values()
        ]

    def to_dict(self) -> dict[str, Any]:
        return {"mutations": self.list_mutations(), "count": len(self._mutations)}
