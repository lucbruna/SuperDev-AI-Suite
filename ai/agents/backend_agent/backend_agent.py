from __future__ import annotations

from typing import Any

from .api_generator import APIGenerator
from .async_optimizer import AsyncOptimizer
from .authentication_generator import AuthenticationGenerator
from .database_mapper import DatabaseMapper
from .middleware_generator import MiddlewareGenerator
from .model_generator import ModelGenerator
from .performance import Performance
from .repository_generator import RepositoryGenerator
from .security import Security
from .service_generator import ServiceGenerator
from .websocket_generator import WebSocketGenerator


class BackendAgent:
    """Central orchestrator for backend code generation."""

    def __init__(self) -> None:
        self._api = APIGenerator()
        self._services = ServiceGenerator()
        self._repositories = RepositoryGenerator()
        self._models = ModelGenerator()
        self._middleware = MiddlewareGenerator()
        self._auth = AuthenticationGenerator()
        self._websocket = WebSocketGenerator()
        self._async_opt = AsyncOptimizer()
        self._perf = Performance()
        self._security = Security()
        self._db_mapper = DatabaseMapper()

    @property
    def api(self) -> APIGenerator:
        return self._api

    @property
    def services(self) -> ServiceGenerator:
        return self._services

    @property
    def repositories(self) -> RepositoryGenerator:
        return self._repositories

    @property
    def models(self) -> ModelGenerator:
        return self._models

    @property
    def middleware(self) -> MiddlewareGenerator:
        return self._middleware

    @property
    def auth(self) -> AuthenticationGenerator:
        return self._auth

    @property
    def websocket(self) -> WebSocketGenerator:
        return self._websocket

    @property
    def async_optimizer(self) -> AsyncOptimizer:
        return self._async_opt

    @property
    def performance(self) -> Performance:
        return self._perf

    @property
    def security(self) -> Security:
        return self._security

    @property
    def database_mapper(self) -> DatabaseMapper:
        return self._db_mapper

    def generate_backend(self, spec: dict[str, Any]) -> dict[str, Any]:
        endpoints = spec.get("endpoints", [])
        for ep in endpoints:
            self._api.add_endpoint(
                ep.get("path", "/"),
                ep.get("method", "GET"),
                ep.get("handler", "handler"),
            )
        services = spec.get("services", [])
        for svc in services:
            self._services.add_service(
                svc.get("name", "Service"),
                svc.get("methods", ["execute"]),
            )
        return {
            "status": "generated",
            "endpoints": self._api.endpoint_count,
            "services": self._services.service_count,
            "models": self._models.model_count,
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "endpoints": self._api.endpoint_count,
            "services": self._services.service_count,
            "repositories": self._repositories.repository_count,
            "models": self._models.model_count,
            "middleware": self._middleware.middleware_count,
            "auth_providers": self._auth.provider_count,
            "websocket_routes": self._websocket.route_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"agent": "backend_agent", "status": self.get_status()}
