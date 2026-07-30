from __future__ import annotations

from typing import Any, Callable

from ..api_events import APIEventBus, APIEventType
from ..api_interfaces import IAPIAuthorizer
from ..api_logger import APILogger
from ..api_models import APIError


class Authorizer(IAPIAuthorizer):
    """Main authorizer delegating to registered engines (RBAC, ABAC, Policies)."""

    def __init__(
        self,
        logger: APILogger | None = None,
        events: APIEventBus | None = None,
        mode: str = "all",
    ) -> None:
        self._logger = logger or APILogger("auth.authorizer")
        self._events = events
        self._engines: list[tuple[str, Callable]] = []
        self._mode = mode  # "all" = AND logic, "any" = OR logic

    def register_engine(self, name: str, engine_fn: Callable) -> None:
        self._engines.append((name, engine_fn))

    async def authorize(self, user: dict[str, Any], action: str, resource: str) -> bool:
        results: list[tuple[str, bool]] = []

        for name, engine_fn in self._engines:
            try:
                result = engine_fn(user, action, resource)
                if hasattr(result, "__await__"):
                    result = await result
                results.append((name, bool(result)))
            except Exception as e:
                self._logger.error("Authorization engine error", engine=name, error=str(e))
                results.append((name, False))

        if self._mode == "any":
            granted = any(r for _, r in results)
        else:
            granted = all(r for _, r in results) if results else True

        if not granted:
            self._logger.warning("Authorization denied", user=user.get("id", ""), action=action, resource=resource)

        if self._events:
            event_type = APIEventType.AUTH_SUCCESS if granted else APIEventType.AUTH_FAILURE
            await self._events.emit(event_type, {"action": action, "resource": resource, "results": results})

        return granted

    def to_dict(self) -> dict[str, Any]:
        return {
            "engines": [n for n, _ in self._engines],
            "mode": self._mode,
        }
