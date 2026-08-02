from __future__ import annotations


class ScopeRegistry:
    """Registers authorization scopes with hierarchical prefix matching.

    Registering a specific scope (e.g. ``read:users:email``) also grants all
    parent scopes (``read:users`` and ``read``).
    """

    def __init__(self) -> None:
        self._scopes: set[str] = set()

    def register(self, scope: str) -> None:
        self._scopes.add(scope)

    def has(self, scope: str) -> bool:
        if scope in self._scopes:
            return True
        prefix = scope + ":"
        return any(s.startswith(prefix) for s in self._scopes)

    def list_scopes(self) -> list[str]:
        return sorted(self._scopes)

    def to_dict(self) -> dict:
        return {"scopes": self.list_scopes(), "count": len(self._scopes)}
