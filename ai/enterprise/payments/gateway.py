"""Payment gateway."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class PaymentGateway:
    def __init__(self) -> None:
        self._gateways: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}

    def register(self, name: str, handler: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        self._gateways[name] = handler

    def process(self, gateway_name: str, payment_data: dict[str, Any]) -> dict[str, Any]:
        handler = self._gateways.get(gateway_name)
        if not handler:
            return {"error": "gateway_not_found", "status": "failed"}
        try:
            return handler(payment_data)
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def list_gateways(self) -> list[str]:
        return list(self._gateways.keys())

    def unregister(self, name: str) -> bool:
        if name in self._gateways:
            del self._gateways[name]
            return True
        return False

    def is_registered(self, name: str) -> bool:
        return name in self._gateways
