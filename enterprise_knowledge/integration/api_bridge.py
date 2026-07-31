"""API bridge mapping engine operations to a REST contract."""

from __future__ import annotations

from typing import Any, Callable

from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics

_Operation = Callable[..., Any]


class ApiBridge:
    """Exposes engine operations as JSON request/response handlers."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None) -> None:
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self._operations: dict[str, _Operation] = {}

    def register(self, name: str, operation: _Operation) -> None:
        self._operations[name] = operation

    def operations(self) -> list[str]:
        return list(self._operations)

    def handle(self, operation: str,
               params: dict[str, Any] | None = None) -> dict[str, Any]:
        func = self._operations.get(operation)
        if func is None:
            return {"ok": False, "error": "unknown_operation",
                    "operation": operation}
        try:
            result = func(**(params or {}))
            self.metrics.increment("ek.api_calls")
            return {"ok": True, "operation": operation, "data": result}
        except TypeError as exc:
            return {"ok": False, "operation": operation,
                    "error": "invalid_params", "detail": str(exc)}
        except Exception as exc:  # noqa: BLE001 - surface as error response
            self.metrics.increment("ek.api_errors")
            return {"ok": False, "operation": operation,
                    "error": "internal", "detail": str(exc)}

    def stats(self) -> dict[str, Any]:
        counters = self.metrics.snapshot()["counters"]
        return {
            "operations": len(self._operations),
            "calls": counters.get("ek.api_calls", 0),
            "errors": counters.get("ek.api_errors", 0),
        }
