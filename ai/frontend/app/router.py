"""
Frontend Router
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RouteType(Enum):
    """Route types."""

    PUBLIC = "public"
    PRIVATE = "private"
    GUEST = "guest"  # Only for non-authenticated users
    ADMIN = "admin"


@dataclass
class Route:
    """Route definition."""

    path: str
    component: Any
    name: str = ""
    type: RouteType = RouteType.PRIVATE
    exact: bool = True
    permissions: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    children: list["Route"] = field(default_factory=list)
    redirect: str | None = None
    before_enter: Callable | None = None
    after_leave: Callable | None = None


@dataclass
class RouteMatch:
    """Matched route result."""

    route: Route
    params: dict[str, str]
    query: dict[str, str]
    hash: str


class Router:
    """Client-side router."""

    def __init__(self):
        self.routes: list[Route] = []
        self.current_route: RouteMatch | None = None
        self.history: list[str] = []
        self.listeners: list[Callable] = []
        self.before_each: list[Callable] = []
        self.after_each: list[Callable] = []
        self.not_found_handler: Callable | None = None

    def add_route(self, route: Route) -> None:
        """Add a route."""
        self.routes.append(route)

    def add_routes(self, routes: list[Route]) -> None:
        """Add multiple routes."""
        self.routes.extend(routes)

    def remove_route(self, path: str) -> None:
        """Remove a route by path."""
        self.routes = [r for r in self.routes if r.path != path]

    def navigate(self, path: str, query: dict[str, str] | None = None) -> bool:
        """Navigate to a path."""
        # Run before each guards
        for guard in self.before_each:
            result = guard(path, self.current_route)
            if result is False:
                return False
            if isinstance(result, str):
                path = result

        # Find matching route
        match = self._match_route(path)
        if not match:
            if self.not_found_handler:
                self.not_found_handler(path)
            return False

        # Update history
        self.history.append(path)

        # Update current route
        old_route = self.current_route
        self.current_route = match

        # Run after each guards
        for guard in self.after_each:
            guard(path, old_route)

        # Notify listeners
        self._notify_listeners()

        return True

    def back(self) -> bool:
        """Go back in history."""
        if len(self.history) > 1:
            self.history.pop()
            previous = self.history[-1]
            self.history.pop()
            return self.navigate(previous)
        return False

    def forward(self) -> bool:
        """Go forward (placeholder)."""
        return False

    def replace(self, path: str) -> bool:
        """Replace current route."""
        if self.history:
            self.history[-1] = path
        return self.navigate(path)

    def _match_route(self, path: str) -> RouteMatch | None:
        """Match a path against routes."""
        for route in self.routes:
            match = self._match_pattern(route.path, path)
            if match is not None:
                return RouteMatch(route=route, params=match, query={}, hash="")
        return None

    def _match_pattern(self, pattern: str, path: str) -> dict[str, str] | None:
        """Match a route pattern against a path."""
        # Convert route pattern to regex
        # Support :param syntax
        param_names = []
        regex_pattern = pattern

        # Find all :param patterns
        param_matches = re.finditer(r":(\w+)", pattern)
        for match in param_matches:
            param_names.append(match.group(1))

        # Convert to regex
        regex_pattern = re.sub(r":(\w+)", r"([^/]+)", regex_pattern)
        regex_pattern = f"^{regex_pattern}$"

        # Match against path
        match = re.match(regex_pattern, path)
        if match:
            params = {}
            for i, name in enumerate(param_names):
                params[name] = match.group(i + 1)
            return params

        return None

    def get_route(self, path: str) -> RouteMatch | None:
        """Get route for a path without navigating."""
        return self._match_route(path)

    def get_current_route(self) -> RouteMatch | None:
        """Get current route."""
        return self.current_route

    def on(self, callback: Callable) -> None:
        """Register route change listener."""
        self.listeners.append(callback)

    def off(self, callback: Callable) -> None:
        """Remove route change listener."""
        self.listeners = [cb for cb in self.listeners if cb != callback]

    def before_each(self, guard: Callable) -> None:
        """Register before each guard."""
        self.before_each.append(guard)

    def after_each(self, guard: Callable) -> None:
        """Register after each guard."""
        self.after_each.append(guard)

    def _notify_listeners(self) -> None:
        """Notify route change listeners."""
        for callback in self.listeners:
            callback(self.current_route)

    def create_link(self, path: str, params: dict[str, str] | None = None) -> str:
        """Create a link from path and params."""
        if params:
            for key, value in params.items():
                path = path.replace(f":{key}", value)
        return path

    def resolve(self, name: str) -> str | None:
        """Resolve route name to path."""
        for route in self.routes:
            if route.name == name:
                return route.path
        return None

    def add_guard(self, before: Callable | None = None, after: Callable | None = None) -> None:
        """Add navigation guards."""
        if before:
            self.before_each.append(before)
        if after:
            self.after_each.append(after)


def create_router(routes: list[Route] | None = None) -> Router:
    """Create a new router with optional routes."""
    router = Router()
    if routes:
        router.add_routes(routes)
    return router
