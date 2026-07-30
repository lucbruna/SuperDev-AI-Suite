from __future__ import annotations

from typing import Any


class APIGenerator:
    """Generates and manages API endpoint definitions."""

    def __init__(self) -> None:
        self._endpoints: dict[str, dict[str, Any]] = {}

    def add_endpoint(
        self,
        path: str,
        method: str,
        handler: str,
        middleware: list[str] | None = None,
    ) -> str:
        key = f"{method}:{path}"
        self._endpoints[key] = {
            "path": path,
            "method": method.upper(),
            "handler": handler,
            "middleware": middleware or [],
        }
        return key

    def get_endpoint(self, path: str, method: str = "GET") -> dict[str, Any] | None:
        return self._endpoints.get(f"{method}:{path}")

    def remove_endpoint(self, path: str, method: str = "GET") -> bool:
        key = f"{method}:{path}"
        if key in self._endpoints:
            del self._endpoints[key]
            return True
        return False

    def list_endpoints(self) -> list[dict[str, Any]]:
        return list(self._endpoints.values())

    @property
    def endpoint_count(self) -> int:
        return len(self._endpoints)

    def generate_routes(self) -> str:
        parts = ["Route Table:", "=" * 40]
        for ep in self._endpoints.values():
            mw = ", ".join(ep["middleware"]) if ep["middleware"] else "none"
            parts.append(f"  {ep['method']:6s} {ep['path']:30s} -> {ep['handler']} [{mw}]")
        return "\n".join(parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "endpoints": list(self._endpoints.values()),
            "endpoint_count": self.endpoint_count,
        }
