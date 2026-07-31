"""
API Gateway Engine - Central API routing
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class Route:
    route_id: str
    path: str
    method: HttpMethod
    target: str
    auth_required: bool = True
    rate_limit: int = 1000
    middleware: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class GatewayRequest:
    request_id: str
    path: str
    method: HttpMethod
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    query_params: Dict[str, str] = field(default_factory=dict)
    client_ip: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GatewayResponse:
    status_code: int
    data: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    duration_ms: float = 0.0


class APIGatewayEngine:
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        self.handlers: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        self.request_log: List[GatewayRequest] = []
        self.rate_counters: Dict[str, int] = {}

    def add_route(self, path: str, method: HttpMethod, target: str, **kwargs) -> Route:
        route_id = hashlib.sha256(f"{method.value}{path}".encode()).hexdigest()[:16]
        route = Route(route_id=route_id, path=path, method=method, target=target, **kwargs)
        self.routes[route_id] = route
        return route

    def remove_route(self, route_id: str) -> bool:
        if route_id in self.routes:
            del self.routes[route_id]
            return True
        return False

    def get_route(self, path: str, method: HttpMethod) -> Optional[Route]:
        for route in self.routes.values():
            if route.path == path and route.method == method and route.enabled:
                return route
        return None

    def register_handler(self, route_id: str, handler: Callable) -> None:
        self.handlers[route_id] = handler

    def add_middleware(self, mw: Callable) -> None:
        self.middleware.append(mw)

    def handle_request(self, request: GatewayRequest) -> GatewayResponse:
        self.request_log.append(request)
        route = self.get_route(request.path, request.method)
        if not route:
            return GatewayResponse(status_code=404, data={"error": "Route not found"})
        if not self._check_rate_limit(route):
            return GatewayResponse(status_code=429, data={"error": "Rate limit exceeded"})
        handler = self.handlers.get(route.route_id)
        if handler:
            try:
                data = handler(request)
                return GatewayResponse(status_code=200, data=data)
            except Exception as e:
                return GatewayResponse(status_code=500, data={"error": str(e)})
        return GatewayResponse(status_code=200, data={"message": "OK"})

    def _check_rate_limit(self, route: Route) -> bool:
        key = route.route_id
        count = self.rate_counters.get(key, 0)
        if count >= route.rate_limit:
            return False
        self.rate_counters[key] = count + 1
        return True

    def list_routes(self) -> List[Route]:
        return list(self.routes.values())

    def get_request_log(self, limit: int = 100) -> List[GatewayRequest]:
        return self.request_log[-limit:]

    def count(self) -> int:
        return len(self.routes)
