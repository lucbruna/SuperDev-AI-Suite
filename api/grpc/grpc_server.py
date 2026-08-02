from __future__ import annotations

import json
from typing import Any, AsyncIterator

from ..api_logger import APILogger
from ..api_metrics import APIMetrics
from ..api_models import APIRequest, APIResponse
from .interceptor import InterceptorChain
from .serializer import GrpcSerializer
from .service import MethodType, ServiceRegistry


class GrpcServer:
    """gRPC server using JSON-RPC-over-HTTP semantics."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 50051,
        logger: APILogger | None = None,
        metrics: APIMetrics | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.registry = ServiceRegistry()
        self.services = self.registry
        self.interceptors = InterceptorChain()
        self._logger = logger or APILogger("grpc.server")
        self._metrics = metrics

    async def handle_unary(self, request: APIRequest) -> APIResponse:
        body = request.body if isinstance(request.body, dict) else {}
        service_name = body.get("service", "")
        method_name = body.get("method", "")
        payload = body.get("payload", {})

        service = self.services.get(service_name)
        if service is None:
            return self._error_response(f"Service not found: {service_name}", request.request_id)

        method = service.get_method(method_name)
        if method is None or method.handler is None:
            return self._error_response(f"Method not found: {method_name}", request.request_id)

        try:
            result = await self.interceptors.intercept(method.handler, payload, request)
            body_str = json.dumps({"result": result}, default=str, ensure_ascii=False)
            return APIResponse(
                status_code=200,
                body=body_str,
                headers={"content-type": "application/json"},
                request_id=request.request_id,
            )
        except Exception as e:
            self._logger.error("gRPC handler error", service=service_name, method=method_name, error=str(e))
            return self._error_response(str(e), request.request_id)

    def _error_response(self, message: str, request_id: str = "") -> APIResponse:
        return APIResponse(
            status_code=500,
            body=json.dumps({"error": {"message": message}}),
            headers={"content-type": "application/json"},
            request_id=request_id,
        )

    async def handle_server_stream(
        self,
        request: APIRequest,
    ) -> AsyncIterator[bytes]:
        body = request.body if isinstance(request.body, dict) else {}
        service_name = body.get("service", "")
        method_name = body.get("method", "")
        payload = body.get("payload", {})

        service = self.services.get(service_name)
        if service is None:
            yield GrpcSerializer.serialize_message({"error": f"Service not found: {service_name}"})
            return

        method = service.get_method(method_name)
        if method is None or method.handler is None:
            yield GrpcSerializer.serialize_message({"error": f"Method not found: {method_name}"})
            return

        result = method.handler(payload, request)
        if hasattr(result, "__aiter__"):
            async for chunk in result:
                yield GrpcSerializer.serialize_message(chunk)
        else:
            yield GrpcSerializer.serialize_message(result)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subsystem": "grpc",
            "services": self.services.to_dict(),
            "interceptors": self.interceptors.to_dict(),
        }
