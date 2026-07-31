"""Security Engine — central orchestrator for all security operations."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .security_config import SecurityConfig, SecurityLevel
from .security_manager import SecurityManager
from .security_events import SecurityEvents
from .security_metrics import SecurityMetrics
from .security_logger import SecurityLogger
from .security_registry import SecurityRegistry
from .security_runtime import SecurityRuntime


class SecurityEngine:
    """Central security engine coordinating all security subsystems."""

    def __init__(self, config: Optional[SecurityConfig] = None) -> None:
        self._config = config or SecurityConfig()
        self._manager = SecurityManager(self._config)
        self._events = SecurityEvents()
        self._metrics = SecurityMetrics()
        self._logger = SecurityLogger()
        self._registry = SecurityRegistry()
        self._runtime = SecurityRuntime()
        self._check_count: int = 0
        self._blocked_count: int = 0

    def check_access(self, user_id: str, resource: str, permission: str) -> Dict[str, Any]:
        self._check_count += 1
        ctx = self._manager.get_context(user_id)
        allowed = ctx is not None and ctx.has_permission(permission)
        if not allowed:
            self._blocked_count += 1
            self._events.emit("access_denied", {"user_id": user_id, "resource": resource})
            self._logger.warn("auth", "Access denied", user_id=user_id, resource=resource)
        else:
            self._events.emit("access_granted", {"user_id": user_id, "resource": resource})
        return {"allowed": allowed, "user_id": user_id, "resource": resource,
                "permission": permission}

    def protect_agent_action(self, agent_id: str, action: str,
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._check_count += 1
        risk_level = self._assess_risk(action, context or {})
        approved = risk_level != "critical"
        self._events.emit("agent_action", {"agent_id": agent_id, "action": action,
                                            "risk": risk_level, "approved": approved})
        self._logger.info("agent_security",
                          f"Agent {agent_id} action {action}: risk={risk_level}")
        self._metrics.increment(f"agent_action_{risk_level}")
        return {"approved": approved, "risk_level": risk_level, "agent_id": agent_id,
                "action": action}

    def _assess_risk(self, action: str, context: Dict[str, Any]) -> str:
        dangerous_actions = {"delete", "drop", "execute", "deploy", "destroy", "modify_security"}
        if action.lower() in dangerous_actions:
            return "high"
        sensitive_actions = {"read_secrets", "access_database", "modify_config"}
        if action.lower() in sensitive_actions:
            return "medium"
        return "low"

    def get_security_status(self) -> Dict[str, Any]:
        return {
            "level": self._config.level.value,
            "total_checks": self._check_count,
            "blocked": self._blocked_count,
            "block_rate": round(self._blocked_count / max(self._check_count, 1), 3),
            "runtime": self._runtime.snapshot(),
            "metrics": self._metrics.get_all(),
        }

    def get_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._events.get_log(limit=limit)

    def get_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._logger.get_entries(limit=limit)
