from __future__ import annotations

from typing import Any


class MiddlewareGenerator:
    """Generates and manages middleware pipeline definitions."""

    def __init__(self) -> None:
        self._middleware: dict[str, dict[str, Any]] = {}

    def add_middleware(self, name: str, order: int, handler: str) -> str:
        self._middleware[name] = {
            "name": name,
            "order": order,
            "handler": handler,
        }
        return name

    def get_middleware(self, name: str) -> dict[str, Any] | None:
        return self._middleware.get(name)

    def remove_middleware(self, name: str) -> bool:
        if name in self._middleware:
            del self._middleware[name]
            return True
        return False

    def list_middleware(self) -> list[dict[str, Any]]:
        return sorted(self._middleware.values(), key=lambda m: m["order"])

    @property
    def middleware_count(self) -> int:
        return len(self._middleware)

    def generate_pipeline(self) -> str:
        if not self._middleware:
            return "(no middleware)"
        sorted_mw = self.list_middleware()
        lines = ["Middleware Pipeline:", "-" * 40]
        for mw in sorted_mw:
            lines.append(f"  [{mw['order']}] {mw['name']:20s} -> {mw['handler']}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "middleware": self.list_middleware(),
            "middleware_count": self.middleware_count,
        }
