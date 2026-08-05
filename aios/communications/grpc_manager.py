"""AIOS gRPC Manager — service descriptor registry.

Registers gRPC-style services (name -> methods) and dispatches calls
locally. Kept deterministic and dependency-free; a deployment may swap
the transport for a real gRPC server without changing the service API.
"""

from __future__ import annotations

import inspect
import time
from typing import Any, Awaitable, Callable

MethodHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]


class GRPCManager:
    """Local gRPC-style service registry and call dispatcher."""

    def __init__(self) -> None:
        self._services: dict[str, dict[str, MethodHandler]] = {}
        self._calls: list[dict[str, Any]] = []

    def register_service(self, service_name: str, methods: dict[str, MethodHandler]) -> "GRPCManager":
        self._services[service_name] = dict(methods)
        return self

    def service_names(self) -> list[str]:
        return sorted(self._services)

    def methods(self, service_name: str) -> list[str]:
        return sorted(self._services.get(service_name, {}))

    async def call(self, service_name: str, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        handler = self._services.get(service_name, {}).get(method)
        if handler is None:
            result: dict[str, Any] = {
                "ok": False,
                "error": f"unknown rpc {service_name}/{method}",
            }
        else:
            try:
                outcome = handler(payload or {})
                if inspect.isawaitable(outcome):
                    outcome = await outcome
                result = {"ok": True, "result": outcome}
            except Exception as exc:  # noqa: BLE001
                result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        self._calls.append(
            {
                "service": service_name,
                "method": method,
                "ok": result.get("ok", False),
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
            }
        )
        return {"service": service_name, "method": method, **result}

    def snapshot(self) -> dict[str, Any]:
        return {
            "services": self.service_names(),
            "calls": len(self._calls),
            "calls_by_service": {
                service: sum(1 for c in self._calls if c["service"] == service)
                for service in self.service_names()
            },
        }
