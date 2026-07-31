from __future__ import annotations

import asyncio
import contextlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentHealthReport:
    agent_id: str
    agent_name: str
    status: str
    is_healthy: bool
    uptime: float
    error_count: int
    last_heartbeat: float | None
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_response_time: float = 0.0
    memory_usage: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class AgentHealthMonitor:
    """Monitors the health and performance of all agents."""

    def __init__(self, check_interval: float = 15.0) -> None:
        self._reports: dict[str, AgentHealthReport] = {}
        self._history: list[dict[str, Any]] = []
        self._check_interval = check_interval
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._response_times: dict[str, list[float]] = {}

    def register_agent(self, agent_id: str, agent_name: str = "") -> None:
        """Register an agent for health monitoring."""
        self._reports[agent_id] = AgentHealthReport(
            agent_id=agent_id,
            agent_name=agent_name or agent_id,
            status="unknown",
            is_healthy=True,
            uptime=0.0,
            error_count=0,
            last_heartbeat=None,
        )
        self._response_times[agent_id] = []

    def unregister_agent(self, agent_id: str) -> None:
        """Remove an agent from monitoring."""
        self._reports.pop(agent_id, None)
        self._response_times.pop(agent_id, None)

    def record_heartbeat(self, agent_id: str, status: str = "running") -> None:
        """Record a heartbeat from an agent."""
        report = self._reports.get(agent_id)
        if report:
            report.last_heartbeat = time.time()
            report.status = status
            report.is_healthy = True

    def record_error(self, agent_id: str, error: str = "") -> None:
        """Record an error for an agent."""
        report = self._reports.get(agent_id)
        if report:
            report.error_count += 1
            report.tasks_failed += 1
            if report.error_count > 5:
                report.is_healthy = False

    def record_task_completed(self, agent_id: str, response_time: float = 0.0) -> None:
        """Record a successful task completion."""
        report = self._reports.get(agent_id)
        if report:
            report.tasks_completed += 1
            if response_time > 0:
                times = self._response_times.setdefault(agent_id, [])
                times.append(response_time)
                if len(times) > 50:
                    times.pop(0)
                report.avg_response_time = sum(times) / len(times)

    def record_uptime(self, agent_id: str, uptime: float) -> None:
        """Record agent uptime."""
        report = self._reports.get(agent_id)
        if report:
            report.uptime = uptime

    def get_report(self, agent_id: str) -> AgentHealthReport | None:
        """Get health report for a specific agent."""
        return self._reports.get(agent_id)

    def get_all_reports(self) -> list[dict[str, Any]]:
        """Get health reports for all agents."""
        return [
            {
                "agent_id": r.agent_id,
                "agent_name": r.agent_name,
                "status": r.status,
                "is_healthy": r.is_healthy,
                "uptime_seconds": round(r.uptime, 1),
                "error_count": r.error_count,
                "tasks_completed": r.tasks_completed,
                "tasks_failed": r.tasks_failed,
                "avg_response_time_ms": round(r.avg_response_time * 1000, 1),
                "last_heartbeat": r.last_heartbeat,
                "heartbeat_age_seconds": round(time.time() - r.last_heartbeat, 1) if r.last_heartbeat else None,
            }
            for r in self._reports.values()
        ]

    def get_unhealthy_agents(self) -> list[dict[str, Any]]:
        """Get list of unhealthy agents."""
        return [
            r for r in self.get_all_reports()
            if not r["is_healthy"]
        ]

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of overall system health."""
        reports = self.get_all_reports()
        total = len(reports)
        healthy = sum(1 for r in reports if r["is_healthy"])
        unhealthy = total - healthy
        return {
            "total_agents": total,
            "healthy": healthy,
            "unhealthy": unhealthy,
            "health_rate": round(healthy / total, 3) if total > 0 else 1.0,
            "total_errors": sum(r["error_count"] for r in reports),
            "total_tasks": sum(r["tasks_completed"] for r in reports),
            "avg_response_time_ms": round(
                sum(r["avg_response_time_ms"] for r in reports) / total, 1
            ) if total > 0 else 0,
        }

    async def start_monitoring(self, health_check_fn: Any = None) -> None:
        """Start the background health monitoring loop."""
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop(health_check_fn))

    async def stop_monitoring(self) -> None:
        """Stop the health monitoring loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _monitor_loop(self, health_check_fn: Any = None) -> None:
        """Background loop that periodically checks agent health."""
        while self._running:
            try:
                await asyncio.sleep(self._check_interval)

                # Check for stale heartbeats
                now = time.time()
                for agent_id, report in self._reports.items():
                    if report.last_heartbeat and (now - report.last_heartbeat) > self._check_interval * 3:
                        report.is_healthy = False
                        report.status = "stale"

                # Run custom health check if provided
                if health_check_fn:
                    try:
                        results = await health_check_fn()
                        for agent_id, is_healthy in results.items():
                            report = self._reports.get(agent_id)
                            if report:
                                report.is_healthy = is_healthy
                    except Exception:
                        pass

                # Record history snapshot
                self._history.append({
                    "timestamp": time.time(),
                    "healthy_count": sum(1 for r in self._reports.values() if r.is_healthy),
                    "total_count": len(self._reports),
                })
                if len(self._history) > 100:
                    self._history = self._history[-50:]

            except asyncio.CancelledError:
                break
            except Exception:
                pass

    def alert_if_unhealthy(self, threshold: float = 0.5) -> list[dict[str, Any]]:
        """Alert if more than threshold percentage of agents are unhealthy."""
        reports = self.get_all_reports()
        if not reports:
            return []
        unhealthy_ratio = sum(1 for r in reports if not r["is_healthy"]) / len(reports)
        if unhealthy_ratio >= threshold:
            return self.get_unhealthy_agents()
        return []

    def get_health_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get health monitoring history."""
        return self._history[-limit:]
