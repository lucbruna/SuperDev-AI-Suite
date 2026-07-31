"""Security Manager — orchestrates all security subsystems."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .security_config import SecurityConfig
from .security_factory import SecurityFactory
from .security_events import SecurityEvents
from .security_metrics import SecurityMetrics
from .security_logger import SecurityLogger
from .security_registry import SecurityRegistry
from .security_runtime import SecurityRuntime
from .security_context import SecurityContext


class SecurityManager:
    """High-level manager coordinating all security operations."""

    def __init__(self, config: Optional[SecurityConfig] = None) -> None:
        self._config = config or SecurityConfig()
        self._factory = SecurityFactory(self._config)
        self._events = self._factory.create_events()
        self._metrics = self._factory.create_metrics()
        self._logger = self._factory.create_logger()
        self._registry = self._factory.create_registry()
        self._runtime = self._factory.create_runtime()
        self._active_contexts: Dict[str, SecurityContext] = {}

    def create_context(self, user_id: str = "", ip_address: str = "") -> SecurityContext:
        ctx = self._factory.create_context()
        if user_id:
            ctx.set_user(user_id)
        if ip_address:
            ctx.set_request(ip_address)
        self._active_contexts[user_id] = ctx
        return ctx

    def get_context(self, user_id: str) -> Optional[SecurityContext]:
        return self._active_contexts.get(user_id)

    def create_session(self, user_id: str, ip_address: str = "") -> Dict[str, Any]:
        session = self._runtime.create_session(user_id, ip_address)
        self._events.emit("session_created", {"user_id": user_id})
        self._logger.info("auth", "Session created", user_id=user_id)
        self._metrics.increment("sessions_created")
        return session

    def invalidate_session(self, session_id: str) -> bool:
        result = self._runtime.invalidate_session(session_id)
        if result:
            self._events.emit("session_invalidated", {"session_id": session_id})
            self._logger.info("auth", "Session invalidated", session_id=session_id)
        return result

    def log_activity(self, user_id: str, action: str, resource: str,
                     details: Optional[Dict[str, Any]] = None) -> None:
        self._logger.info("audit", f"{action} on {resource}",
                          user_id=user_id, **(details or {}))
        self._metrics.increment(f"action_{action}")
        self._events.emit("activity", {"user_id": user_id, "action": action,
                                        "resource": resource})

    def get_metrics(self) -> Dict[str, Any]:
        return {
            **self._metrics.get_all(),
            "runtime": self._runtime.snapshot(),
            "registry": self._registry.count(),
            "active_contexts": len(self._active_contexts),
        }

    def get_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._events.get_log(limit=limit)

    def get_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._logger.get_entries(limit=limit)
