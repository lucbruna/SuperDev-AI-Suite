from __future__ import annotations

import asyncio
from typing import Any

from .api_interfaces import IAPIServer
from .api_models import APIRequest, APIResponse
from .api_runtime import APIRuntime


class APIServer(IAPIServer):
    """WSGI/ASGI server abstraction for the API Engine."""

    def __init__(self, runtime: APIRuntime, host: str = "0.0.0.0", port: int = 8000) -> None:
        self._runtime = runtime
        self._host = host
        self._port = port
        self._running = False
        self._server: Any = None

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def is_running(self) -> bool:
        return self._running

    async def serve(self, host: str | None = None, port: int | None = None) -> None:
        self._host = host or self._host
        self._port = port or self._port
        self._running = True

        class _App:
            def __init__(self, runtime: APIRuntime) -> None:
                self._runtime = runtime

            async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
                if scope["type"] == "http":
                    await self._handle_http(scope, receive, send)

            async def _handle_http(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
                request = APIRequest(
                    method=scope.get("method", "GET"),
                    path=scope.get("path", "/"),
                    headers={k.decode(): v.decode() for k, v in scope.get("headers", [])},
                    request_id=scope.get("request_id", ""),
                )
                response = await self._runtime.process_request(request)
                await send({
                    "type": "http.response.start",
                    "status": response.status_code,
                    "headers": [(k.lower().encode(), v.encode()) for k, v in response.headers.items()],
                })
                await send({
                    "type": "http.response.body",
                    "body": str(response.body).encode() if response.body else b"",
                })

        app = _App(self._runtime)
        try:
            import uvicorn  # type: ignore[import-untyped]
            config = uvicorn.Config(app, host=self._host, port=self._port, log_level="info")
            server = uvicorn.Server(config)
            self._server = server
            await server.serve()
        except ImportError:
            import http.server
            import json

            class Handler(http.server.BaseHTTPRequestHandler):
                def do_GET(self) -> None:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "running"}).encode())

                def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
                    pass

            with http.server.HTTPServer((self._host, self._port), Handler) as httpd:
                self._server = httpd
                httpd.serve_forever()

    async def stop(self) -> None:
        self._running = False
        if self._server is not None:
            if hasattr(self._server, "should_exit"):
                self._server.should_exit = True
            elif hasattr(self._server, "shutdown"):
                self._server.shutdown()

    def to_dict(self) -> dict[str, Any]:
        return {
            "host": self._host,
            "port": self._port,
            "running": self._running,
        }
