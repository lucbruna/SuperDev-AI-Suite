from __future__ import annotations

from typing import Any


class WebSocketGenerator:
    """Generates and manages WebSocket route definitions."""

    def __init__(self) -> None:
        self._routes: dict[str, dict[str, Any]] = {}

    def add_route(
        self,
        path: str,
        handler: str,
        events: list[str] | None = None,
    ) -> str:
        self._routes[path] = {
            "path": path,
            "handler": handler,
            "events": events or ["connect", "disconnect", "message"],
        }
        return path

    def get_route(self, path: str) -> dict[str, Any] | None:
        return self._routes.get(path)

    def remove_route(self, path: str) -> bool:
        if path in self._routes:
            del self._routes[path]
            return True
        return False

    def list_routes(self) -> list[dict[str, Any]]:
        return list(self._routes.values())

    @property
    def route_count(self) -> int:
        return len(self._routes)

    def generate_handler_code(self, path: str) -> str:
        route = self._routes.get(path)
        if route is None:
            return f"# Route '{path}' not found"
        events_code = "\n".join(
            f"    async def on_{evt}(self, **kwargs: Any) -> None:\n        ..."
            for evt in route["events"]
        )
        handler_name = route["handler"]
        return (
            f"from __future__ import annotations\n\nfrom typing import Any\n\n\n"
            f"class {handler_name}:\n\n    def __init__(self) -> None:\n"
            f'        self._path = "{path}"\n\n{events_code}\n'
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "routes": list(self._routes.values()),
            "route_count": self.route_count,
        }
