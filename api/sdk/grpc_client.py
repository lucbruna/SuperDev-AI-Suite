from __future__ import annotations

from typing import Any

from .client import BaseClient


class GrpcClient(BaseClient):
    """gRPC-style client using JSON-RPC over HTTP.

    Provides unary, server-streaming, client-streaming, and bidirectional
    interaction patterns through a JSON-RPC transport.
    """

    def unary(self, service: str, method: str, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Unary RPC: single request, single response."""
        body: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": f"{service}/{method}",
            "params": request or {},
            "id": 1,
        }
        return self.request("POST", "/grpc", body=body, **kwargs)

    def server_stream(self, service: str, method: str, request: dict[str, Any] | None = None, **kwargs: Any) -> list[Any]:
        """Server-streaming RPC: single request, multiple responses."""
        body: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": f"{service}/{method}",
            "params": {**(request or {}), "_stream": "server"},
            "id": 1,
        }
        result = self.request("POST", "/grpc", body=body, **kwargs)
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "items" in result:
            return result["items"]
        return [result]

    def client_stream(self, service: str, method: str, items: list[dict[str, Any]], **kwargs: Any) -> Any:
        """Client-streaming RPC: multiple requests, single response."""
        body: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": f"{service}/{method}",
            "params": {"_stream": "client", "items": items},
            "id": 1,
        }
        return self.request("POST", "/grpc", body=body, **kwargs)

    def bidi_stream(self, service: str, method: str, items: list[dict[str, Any]], **kwargs: Any) -> list[Any]:
        """Bidirectional streaming RPC: multiple requests, multiple responses."""
        body: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": f"{service}/{method}",
            "params": {"_stream": "bidi", "items": items},
            "id": 1,
        }
        result = self.request("POST", "/grpc", body=body, **kwargs)
        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "items" in result:
            return result["items"]
        return [result]
