from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class IAPIApplication(ABC):
    @abstractmethod
    async def startup(self) -> None: ...
    @abstractmethod
    async def shutdown(self) -> None: ...
    @abstractmethod
    def get_server(self) -> Any: ...


class IAPIRouter(ABC):
    @abstractmethod
    def register_routes(self, app: Any) -> None: ...
    @abstractmethod
    def get_routes(self) -> dict[str, Any]: ...


class IAPIAuthenticator(ABC):
    @abstractmethod
    async def authenticate(self, request: Any) -> dict[str, Any]: ...
    @abstractmethod
    async def validate_token(self, token: str) -> dict[str, Any]: ...


class IAPIAuthorizer(ABC):
    @abstractmethod
    async def authorize(self, user: dict[str, Any], action: str, resource: str) -> bool: ...


class IAPIValidator(ABC):
    @abstractmethod
    async def validate(self, data: Any, schema: Any) -> dict[str, Any]: ...


class IAPISerializer(ABC):
    @abstractmethod
    def serialize(self, data: Any, fmt: str = "json") -> Any: ...
    @abstractmethod
    def deserialize(self, data: Any, fmt: str = "json") -> Any: ...


class IAPIMiddleware(ABC):
    @abstractmethod
    async def before_request(self, request: Any) -> Any: ...
    @abstractmethod
    async def after_request(self, response: Any) -> Any: ...


class IAPIRateLimiter(ABC):
    @abstractmethod
    async def check_rate_limit(self, key: str, max_requests: int, window_sec: int) -> bool: ...


class IAPICache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None: ...
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None: ...
    @abstractmethod
    async def invalidate(self, key: str) -> bool: ...


class IAPIMetrics(ABC):
    @abstractmethod
    def increment(self, metric: str, tags: dict[str, str] | None = None) -> None: ...
    @abstractmethod
    def timing(self, metric: str, duration_ms: float, tags: dict[str, str] | None = None) -> None: ...


class IAPILogger(ABC):
    @abstractmethod
    def info(self, msg: str, **kwargs: Any) -> None: ...
    @abstractmethod
    def error(self, msg: str, **kwargs: Any) -> None: ...
    @abstractmethod
    def warning(self, msg: str, **kwargs: Any) -> None: ...


class IAPIServer(ABC):
    @abstractmethod
    async def serve(self, host: str, port: int) -> None: ...
    @abstractmethod
    async def stop(self) -> None: ...


class IAPIGateway(ABC):
    @abstractmethod
    async def forward(self, request: Any, target: str) -> Any: ...
    @abstractmethod
    def register_service(self, name: str, url: str) -> None: ...
