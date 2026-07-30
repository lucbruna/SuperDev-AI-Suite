from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ..api_interfaces import IAPIGateway
from ..api_logger import APILogger
from ..api_metrics import APIMetrics
from ..api_models import APIRequest, APIResponse
from .router import GatewayRouter


class APIGateway(IAPIGateway):
    """API Gateway: routes requests to registered backend services."""

    def __init__(self, logger: APILogger | None = None, metrics: APIMetrics | None = None) -> None:
        self._services: dict[str, str] = {}
        self._router = GatewayRouter(logger=logger)
        self._logger = logger or APILogger("gateway")
        self._metrics = metrics

    @property
    def router(self) -> GatewayRouter:
        return self._router

    def register_service(self, name: str, url: str) -> None:
        self._services[name] = url
        self._logger.info("Service registered", name=name, url=url)

    def get_service_url(self, name: str) -> str | None:
        return self._services.get(name)

    def register_route(self, path_prefix: str, service_name: str) -> None:
        target = self._services.get(service_name)
        if target:
            self._router.register(path_prefix, target)
            self._logger.info("Gateway route registered", prefix=path_prefix, target=target)

    async def forward(self, request: Any, target: str) -> APIResponse:
        method = getattr(request, "method", "GET")
        path = getattr(request, "path", "/")
        headers = getattr(request, "headers", {}) if hasattr(request, "headers") else {}
        body = getattr(request, "body", None)

        url = f"{target}{path}"
        data = None
        if body is not None:
            if isinstance(body, dict):
                data = json.dumps(body).encode("utf-8")
            elif isinstance(body, str):
                data = body.encode("utf-8")
            else:
                data = body

        try:
            req = urllib.request.Request(
                url,
                data=data,
                method=method,
                headers={
                    "Content-Type": headers.get("content-type", "application/json") if isinstance(headers, dict) else "application/json",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                response_body = resp.read().decode("utf-8")
                return APIResponse(
                    status_code=resp.status,
                    body=response_body,
                    headers={"content-type": resp.headers.get("Content-Type", "application/json")},
                )
        except urllib.error.HTTPError as e:
            return APIResponse(
                status_code=e.code,
                body=json.dumps({"error": str(e.reason)}),
                headers={"content-type": "application/json"},
            )
        except Exception as e:
            self._logger.error("Gateway forward error", target=target, error=str(e))
            return APIResponse(
                status_code=502,
                body=json.dumps({"error": "Bad Gateway", "detail": str(e)}),
                headers={"content-type": "application/json"},
            )

    def list_services(self) -> dict[str, str]:
        return dict(self._services)

    def to_dict(self) -> dict[str, Any]:
        return {
            "gateway": "APIGateway",
            "services": self.list_services(),
            "routes": self._router.to_dict(),
        }
