from __future__ import annotations

import logging
from typing import Any

from .caching import GatewayCache
from .filtering import RequestFilter
from .load_balancing import LoadBalancer
from .monitoring import GatewayMonitoring
from .rate_limit import RateLimiter
from .request_router import RequestRouter
from .security import GatewaySecurity


class GatewayEngine:
    """API Gateway: routes, limits, filters, caches, balances, and monitors traffic."""

    def __init__(
        self,
        rate_limit: int = 100,
        cache_ttl: float = 60.0,
        window: float = 60.0,
    ) -> None:
        self._log = logging.getLogger("superdev.integration.gateway")
        self.router = RequestRouter()
        self.rate_limiter = RateLimiter(rate_limit, window)
        self.balancer = LoadBalancer()
        self.cache = GatewayCache(ttl=cache_ttl)
        self.filter = RequestFilter()
        self.monitoring = GatewayMonitoring()
        self.security = GatewaySecurity()

    def route(self, method: str, path: str, handler: Any) -> None:
        self.router.register(method, path, handler)

    def handle(self, method: str, path: str, headers: dict[str, str] | None = None,
               params: dict[str, Any] | None = None,
               client_ip: str = "", client_id: str = "default") -> Any:
        """Processes an inbound request through the gateway pipeline."""
        headers = headers or {}
        params = params or {}

        if not self.filter.allow(method, path, headers, client_ip):
            raise PermissionError(f"request blocked: {method.upper()} {path}")

        if not self.rate_limiter.allow(client_id):
            raise RuntimeError("rate limit exceeded")

        self.security.enforce(headers, required=False)

        cache_key = f"{method.upper()} {path} {sorted(params.items())}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        import time

        start = time.monotonic()
        try:
            result = self.router.dispatch(method, path, params)
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            status = "error"
            result = {"error": str(exc)}
        self.monitoring.record_request(f"{method.upper()} {path}", time.monotonic() - start, status)

        if status == "ok":
            self.cache.set(cache_key, result)
        return result

    def add_target(self, target: str) -> None:
        self.balancer.add_target(target)

    def register_key(self, api_key: str, owner: str = "anonymous") -> None:
        self.security.register_key(api_key, owner)

    def stats(self) -> dict[str, Any]:
        return {
            "routes": len(self.router.routes()),
            "targets": self.balancer.count(),
            "cache_entries": self.cache.size(),
            "rate_limit": self.rate_limiter.snapshot(),
            "monitoring": self.monitoring.snapshot(),
        }
