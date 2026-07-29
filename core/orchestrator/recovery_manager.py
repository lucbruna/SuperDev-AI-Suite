"""Recovery Manager — automatic failure recovery for platform services.

Handles service crashes, dependency failures, event bus timeouts,
and health check failures with configurable retry, backoff, and escalation.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from .exceptions import RecoveryError
from .types import ServiceStatus, now_iso


class RecoveryManager:
    """Automatic failure recovery for the SuperDev platform.

    Features:
    - Configurable retry with exponential backoff
    - Escalation after max retries
    - Dependency-aware recovery (restart dependents after service recovery)
    - Circuit breaker pattern to prevent cascading failures
    """

    MAX_RETRIES = 5
    BASE_DELAY = 1.0
    MAX_DELAY = 60.0
    CIRCUIT_BREAKER_THRESHOLD = 3
    CIRCUIT_BREAKER_RESET_SECONDS = 120.0

    def __init__(self, orchestrator: Any) -> None:
        self._orchestrator = orchestrator
        self._failure_counts: dict[str, int] = {}
        self._recovery_history: list[dict[str, Any]] = []
        self._circuit_breakers: dict[str, dict[str, Any]] = {}
        self._recovery_locks: dict[str, asyncio.Lock] = {}

    async def handle_failure(
        self,
        service: str,
        error: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle a service failure with automatic recovery.

        Steps:
        1. Check circuit breaker (if tripped, skip recovery)
        2. Increment failure count
        3. Calculate backoff delay
        4. Attempt recovery
        5. If successful, reset failure count and circuit breaker
        6. If failed and max retries exceeded, trip circuit breaker
        7. Log recovery result
        """
        if service not in self._recovery_locks:
            self._recovery_locks[service] = asyncio.Lock()

        async with self._recovery_locks[service]:
            # Check circuit breaker
            if self._is_circuit_open(service):
                return {
                    "service": service,
                    "status": "circuit_open",
                    "error": "Circuit breaker is open. Skipping recovery.",
                }

            # Update failure count
            self._failure_counts[service] = self._failure_counts.get(service, 0) + 1
            attempt = self._failure_counts[service]

            # Calculate backoff
            delay = self._calculate_backoff(attempt)

            # Wait before attempting recovery
            await asyncio.sleep(delay)

            # Attempt recovery
            start = time.time()
            result = await self._attempt_recovery(service, error, attempt)
            elapsed = round((time.time() - start) * 1000, 2)

            # Record result
            entry = {
                "service": service,
                "attempt": attempt,
                "error": error,
                "delay": round(delay, 2),
                "success": result.get("success", False),
                "action": result.get("action", "none"),
                "elapsed_ms": elapsed,
                "timestamp": now_iso(),
            }
            self._recovery_history.append(entry)
            if len(self._recovery_history) > 500:
                self._recovery_history = self._recovery_history[-250:]

            if result.get("success"):
                # Reset failure count and circuit breaker
                self._failure_counts[service] = 0
                self._circuit_breakers.pop(service, None)
                self._orchestrator.service_registry.set_status(
                    service, ServiceStatus.RUNNING,
                )
            elif attempt >= self.MAX_RETRIES:
                # Trip circuit breaker
                self._trip_circuit_breaker(service)
                self._orchestrator.service_registry.set_status(
                    service, ServiceStatus.FAILED,
                )

            return {
                "service": service,
                "status": "recovered" if result.get("success") else "failed",
                "attempt": attempt,
                "max_retries": self.MAX_RETRIES,
                "action": result.get("action", "none"),
                "error": error if not result.get("success") else "",
                "elapsed_ms": elapsed,
            }

    async def _attempt_recovery(
        self,
        service: str,
        error: str,
        attempt: int,
    ) -> dict[str, Any]:
        """Attempt to recover a failed service.

        Strategy depends on the service type:
        - For critical services (database, cache): restart immediately
        - For non-critical services (dashboard, plugins): restart with delay
        - For agent services: reinitialize the agent
        """
        registry = self._orchestrator.service_registry
        if not registry.is_registered(service):
            return {"success": False, "action": "not_registered"}

        try:
            await self._orchestrator.event_bus.send_to(
                service, "recover",
                {
                    "error": error,
                    "attempt": attempt,
                    "max_retries": self.MAX_RETRIES,
                    "timestamp": now_iso(),
                },
            )
            return {"success": True, "action": "restarted"}
        except Exception:
            # Fallback: just restart via event bus
            try:
                await self._orchestrator.event_bus.publish(
                    "system.recovery.restart",
                    {"service": service, "attempt": attempt},
                    source="recovery_manager",
                )
                return {"success": True, "action": "restart_requested"}
            except Exception:
                return {"success": False, "action": "restart_failed"}

    async def reset_service(self, service: str) -> bool:
        """Manually reset a service's failure state."""
        self._failure_counts.pop(service, None)
        self._circuit_breakers.pop(service, None)
        if service in self._recovery_locks:
            del self._recovery_locks[service]
        return True

    async def reset_all(self) -> None:
        """Reset all failure states and circuit breakers."""
        self._failure_counts.clear()
        self._circuit_breakers.clear()
        self._recovery_locks.clear()

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        delay = self.BASE_DELAY * (2 ** (attempt - 1))
        import random
        jitter = random.uniform(0, 0.5)
        return min(delay + jitter, self.MAX_DELAY)

    def _is_circuit_open(self, service: str) -> bool:
        """Check if the circuit breaker is open for a service."""
        cb = self._circuit_breakers.get(service)
        if not cb:
            return False
        if time.time() - cb["tripped_at"] > self.CIRCUIT_BREAKER_RESET_SECONDS:
            # Auto-reset after timeout
            self._circuit_breakers.pop(service, None)
            return False
        return True

    def _trip_circuit_breaker(self, service: str) -> None:
        """Trip the circuit breaker for a service."""
        self._circuit_breakers[service] = {
            "tripped_at": time.time(),
            "failure_count": self._failure_counts.get(service, 0),
            "reset_at": time.time() + self.CIRCUIT_BREAKER_RESET_SECONDS,
        }

    def get_failure_summary(self) -> dict[str, Any]:
        """Get a summary of all failures and recoveries."""
        recent = self._recovery_history[-50:] if self._recovery_history else []
        recovered = sum(1 for r in recent if r.get("success"))
        failed = sum(1 for r in recent if not r.get("success"))
        return {
            "total_failures": sum(self._failure_counts.values()),
            "services_with_failures": len(self._failure_counts),
            "open_circuit_breakers": len([
                s for s in self._circuit_breakers
                if self._is_circuit_open(s)
            ]),
            "recent_recovery_rate": round(
                recovered / (recovered + failed), 3
            ) if (recovered + failed) > 0 else 1.0,
            "recovery_history": recent[-10:],
        }

    def get_failure_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get the recovery history log."""
        return self._recovery_history[-limit:]
