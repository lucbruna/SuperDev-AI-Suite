from __future__ import annotations

from typing import Any


class RouterGenerator:
    """Generates and manages route definitions."""

    def __init__(self) -> None:
        self._routes: dict[str, dict[str, Any]] = {}

    def add_route(self, path: str, component: str, guards: list[str] | None = None) -> str:
        self._routes[path] = {
            "path": path,
            "component": component,
            "guards": guards or [],
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

    def generate_router_code(self) -> str:
        if not self._routes:
            return "// No routes defined"
        route_imports = "\n".join(
            f"import {r['component']} from './pages/{r['component']}';"
            for r in self._routes.values()
        )
        route_defs = "\n".join(
            f"  {{ path: '{r['path']}', element: <{r['component']} /> }},"
            for r in self._routes.values()
        )
        return (
            f"import React from 'react';\n"
            f"import {{ Routes, Route }} from 'react-router-dom';\n"
            f"{route_imports}\n\n"
            f"const AppRoutes: React.FC = () => (\n"
            f"  <Routes>\n"
            f"{route_defs}\n"
            f"  </Routes>\n"
            f");\n\n"
            f"export default AppRoutes;\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "routes": list(self._routes.values()),
            "route_count": self.route_count,
        }
