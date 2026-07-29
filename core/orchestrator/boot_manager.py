"""Boot Manager — executes the platform startup sequence.

Manages the ordered initialization of all system services according to
their dependency graph, with timeout and retry logic.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from .exceptions import BootError, BootTimeoutError
from .types import (
    BootConfig,
    HealthReport,
    ServiceCategory,
    ServiceStatus,
    now_iso,
)


class BootManager:
    """Manages the system boot sequence.

    Boot order (as specified):
    1. Load configuration
    2. Initialize Logger
    3. Initialize Database
    4. Initialize Cache
    5. Initialize Queues
    6. Initialize API
    7. Initialize AI
    8. Initialize Plugins
    9. Initialize Dashboard
    10. Initialize Scheduler
    11. Initialize Monitoring
    12. System ONLINE
    """

    # Standard boot phase order
    BOOT_PHASES: list[tuple[str, ServiceCategory]] = [
        ("core.logger", ServiceCategory.CORE),
        ("database.postgres", ServiceCategory.DATABASE),
        ("cache.redis", ServiceCategory.CACHE),
        ("queue.rabbitmq", ServiceCategory.QUEUE),
        ("api.fastapi", ServiceCategory.API),
        ("ai.engine", ServiceCategory.AI),
        ("ai.agents", ServiceCategory.AGENT),
        ("plugins.loader", ServiceCategory.PLUGIN),
        ("workflow.engine", ServiceCategory.WORKFLOW),
        ("dashboard.web", ServiceCategory.DASHBOARD),
        ("integration.storage", ServiceCategory.INTEGRATION),
        ("monitoring.health", ServiceCategory.MONITORING),
        ("core.scheduler", ServiceCategory.SCHEDULER),
    ]

    def __init__(self, orchestrator: Any) -> None:
        self._orchestrator = orchestrator
        self._boot_results: dict[str, dict[str, Any]] = {}

    async def execute_boot_sequence(self, config: BootConfig) -> dict[str, Any]:
        """Execute the full boot sequence for all services."""
        start_time = time.time()
        total = len(self.BOOT_PHASES)
        completed = 0
        failed: list[str] = []
        has_errors = False

        event_bus = self._orchestrator.event_bus
        registry = self._orchestrator.service_registry

        await event_bus.publish("system.boot.starting", {
            "total_phases": total, "config": config.__dict__,
        }, source="boot_manager")

        for phase_name, category in self.BOOT_PHASES:
            if config.safe_mode and category in (ServiceCategory.PLUGIN, ServiceCategory.AI):
                registry.set_status(phase_name, ServiceStatus.SKIPPED)
                self._boot_results[phase_name] = {
                    "status": "skipped", "reason": "safe mode",
                }
                continue

            phase_start = time.time()
            try:
                await event_bus.publish("system.boot.phase", {
                    "phase": phase_name, "category": category.name,
                }, source="boot_manager")

                success = await self._boot_service(
                    phase_name, category, config.timeout_seconds,
                )

                if success:
                    registry.set_status(phase_name, ServiceStatus.RUNNING)
                    completed += 1
                    self._boot_results[phase_name] = {
                        "status": "ok",
                        "time_ms": round((time.time() - phase_start) * 1000, 2),
                    }
                else:
                    registry.set_status(phase_name, ServiceStatus.FAILED)
                    failed.append(phase_name)
                    self._boot_results[phase_name] = {
                        "status": "failed", "error": "Service did not start",
                    }
                    has_errors = True
                    if not config.safe_mode:
                        raise BootError(phase_name, "Boot sequence aborted")

            except BootTimeoutError:
                registry.set_status(phase_name, ServiceStatus.FAILED)
                failed.append(phase_name)
                self._boot_results[phase_name] = {
                    "status": "timeout", "error": f"Exceeded {config.timeout_seconds}s",
                }
                has_errors = True
                if not config.safe_mode:
                    break

            except Exception as e:
                registry.set_status(phase_name, ServiceStatus.FAILED)
                failed.append(phase_name)
                self._boot_results[phase_name] = {
                    "status": "error", "error": str(e),
                }
                has_errors = True
                if not config.safe_mode:
                    break

        total_time = round(time.time() - start_time, 3)

        await event_bus.publish("system.boot.completed", {
            "success": not has_errors,
            "total_phases": total,
            "completed": completed,
            "failed": len(failed),
            "failed_services": failed,
            "total_time": total_time,
            "results": self._boot_results,
        }, source="boot_manager")

        return {
            "success": not has_errors,
            "total_phases": total,
            "completed": completed,
            "failed": failed,
            "total_time": total_time,
            "results": self._boot_results,
        }

    async def _boot_service(
        self, name: str, category: ServiceCategory, timeout: float,
    ) -> bool:
        """Initialize a single service with retry logic."""
        for attempt in range(3):
            try:
                async with asyncio.timeout(timeout):
                    await self._orchestrator.event_bus.send_to(
                        name, "initialize",
                        {"category": category.name, "attempt": attempt + 1},
                    )
                return True
            except TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise BootTimeoutError(name, timeout)
            except Exception:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
        return False

    async def check_service_health(self, name: str) -> HealthReport:
        """Check the health of a specific service."""
        import time as tmod
        start = tmod.time()
        try:
            async with asyncio.timeout(5.0):
                await self._orchestrator.event_bus.send_to(name, "healthcheck", {})
            response_time = (tmod.time() - start) * 1000
            return HealthReport(
                service_name=name,
                status=ServiceStatus.RUNNING,
                is_healthy=True,
                response_time_ms=round(response_time, 2),
            )
        except Exception:
            return HealthReport(
                service_name=name,
                status=ServiceStatus.FAILED,
                is_healthy=False,
                message="Health check timed out or failed",
            )
