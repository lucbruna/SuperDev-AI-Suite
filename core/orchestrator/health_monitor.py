"""Health Monitor — dedicated service health monitoring for the platform.

Extracted from the inline _health_loop() in orchestrator.py into its own
component with configurable checks, alerting thresholds, and history tracking.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from .types import HealthReport, ServiceStatus, now_iso


class HealthMonitor:
    """Dedicated health monitoring service.

    Periodically checks all registered services, tracks health history,
    detects degradation patterns, and emits health events.
    """

    def __init__(self, event_bus: Any = None) -> None:
        self._event_bus = event_bus
        self._service_registry: Any = None
        self._recovery_manager: Any = None
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._interval: float = 30.0
        self._health_history: dict[str, list[HealthReport]] = {}
        self._consecutive_failures: dict[str, int] = {}
        self._alert_threshold: int = 3

    def configure(
        self,
        service_registry: Any,
        recovery_manager: Any,
        interval: float = 30.0,
        alert_threshold: int = 3,
    ) -> None:
        """Configure the health monitor with dependencies."""
        self._service_registry = service_registry
        self._recovery_manager = recovery_manager
        self._interval = interval
        self._alert_threshold = alert_threshold

    async def start(self) -> None:
        """Start the periodic health monitoring loop."""
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        """Stop the health monitoring loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def check_service(self, service_name: str) -> HealthReport:
        """Check the health of a single service."""
        start = time.time()
        try:
            async with asyncio.timeout(5.0):
                if self._event_bus:
                    await self._event_bus.send_to(service_name, "healthcheck", {})
                response_time = (time.time() - start) * 1000
                report = HealthReport(
                    service_name=service_name,
                    status=ServiceStatus.RUNNING,
                    is_healthy=True,
                    response_time_ms=round(response_time, 2),
                    last_heartbeat=time.time(),
                )
        except (asyncio.TimeoutError, Exception) as e:
            report = HealthReport(
                service_name=service_name,
                status=ServiceStatus.FAILED,
                is_healthy=False,
                message=str(e) if not isinstance(e, asyncio.TimeoutError) else "Health check timed out",
            )

        self._record_health(service_name, report)
        return report

    async def check_all(self) -> dict[str, HealthReport]:
        """Check health of all registered services."""
        if not self._service_registry:
            return {}

        services = self._service_registry.list_services()
        reports = {}

        async def check(svc: dict[str, Any]) -> None:
            name = svc["name"]
            reports[name] = await self.check_service(name)

        tasks = [check(svc) for svc in services]
        await asyncio.gather(*tasks, return_exceptions=True)

        return reports

    def get_service_history(self, service_name: str, limit: int = 10) -> list[HealthReport]:
        """Get recent health reports for a service."""
        return self._health_history.get(service_name, [])[-limit:]

    def get_unhealthy_services(self) -> list[dict[str, Any]]:
        """Get services currently marked as unhealthy."""
        unhealthy = []
        for service_name, failures in self._consecutive_failures.items():
            if failures >= self._alert_threshold:
                history = self._health_history.get(service_name, [])
                last = history[-1] if history else None
                unhealthy.append({
                    "service": service_name,
                    "consecutive_failures": failures,
                    "last_error": last.message if last else "Unknown",
                    "last_check": last.last_heartbeat if last else 0,
                })
        return unhealthy

    def get_summary(self) -> dict[str, Any]:
        """Get overall health summary."""
        total = 0
        healthy = 0
        unhealthy_services = self.get_unhealthy_services()

        for history in self._health_history.values():
            if history:
                total += 1
                if history[-1].is_healthy:
                    healthy += 1

        return {
            "total_monitored": total,
            "healthy": healthy,
            "unhealthy": len(unhealthy_services),
            "health_rate": round(healthy / total, 3) if total > 0 else 1.0,
            "unhealthy_services": unhealthy_services,
        }

    async def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(self._interval)
                reports = await self.check_all()

                # Process results
                for service_name, report in reports.items():
                    if not report.is_healthy:
                        count = self._consecutive_failures.get(service_name, 0) + 1
                        self._consecutive_failures[service_name] = count

                        if count >= self._alert_threshold:
                            if self._event_bus:
                                await self._event_bus.publish(
                                    "health.alert",
                                    {
                                        "service": service_name,
                                        "failures": count,
                                        "message": report.message,
                                    },
                                    source="health_monitor",
                                )
                            if self._recovery_manager:
                                await self._recovery_manager.handle_failure(
                                    service=service_name,
                                    error=report.message,
                                    context={},
                                )
                    else:
                        self._consecutive_failures.pop(service_name, None)

                if self._event_bus:
                    await self._event_bus.publish(
                        "health.tick",
                        {
                            "checked": len(reports),
                            "healthy": sum(1 for r in reports.values() if r.is_healthy),
                            "unhealthy": sum(1 for r in reports.values() if not r.is_healthy),
                        },
                        source="health_monitor",
                    )

            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def _record_health(self, service_name: str, report: HealthReport) -> None:
        """Record a health report for a service."""
        if service_name not in self._health_history:
            self._health_history[service_name] = []
        history = self._health_history[service_name]
        history.append(report)
        if len(history) > 100:
            history.pop(0)

    def get_statistics(self) -> dict[str, Any]:
        """Get health monitor statistics."""
        return {
            "is_running": self._running,
            "check_interval": self._interval,
            "alert_threshold": self._alert_threshold,
            "services_monitored": len(self._health_history),
            "services_with_failures": len(self._consecutive_failures),
            "total_checks": sum(len(h) for h in self._health_history.values()),
        }
