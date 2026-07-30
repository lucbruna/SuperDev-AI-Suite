from __future__ import annotations

from typing import Any

from ..api_interfaces import IAPIRouter
from ..api_logger import APILogger


class GatewayRouter(IAPIRouter):
    """Gateway-level routing: maps inbound requests to backend services."""

    def __init__(self, logger: APILogger | None = None) -> None:
        self._routes: list[dict[str, Any]] = []
        self._logger = logger or APILogger("gateway.router")

    def register(self, path_prefix: str, target_url: str, methods: list[str] | None = None) -> None:
        self._routes.append({
            "prefix": path_prefix,
            "target": target_url,
            "methods": methods or ["GET", "POST", "PUT", "PATCH", "DELETE"],
        })

    def match(self, path: str, method: str) -> dict[str, Any] | None:
        for route in self._routes:
            if path.startswith(route["prefix"]):
                if method.upper() in route["methods"]:
                    remaining = path[len(route["prefix"]):]
                    return {
                        "target": route["target"],
                        "remaining_path": remaining,
                        "prefix": route["prefix"],
                    }
        return None

    def register_routes(self, app: Any) -> None:
        pass

    def get_routes(self) -> dict[str, Any]:
        return {r["prefix"]: r["target"] for r in self._routes}

    def to_dict(self) -> dict[str, Any]:
        return {
            "routes": [{"prefix": r["prefix"], "target": r["target"], "methods": r["methods"]} for r in self._routes],
            "count": len(self._routes),
        }
