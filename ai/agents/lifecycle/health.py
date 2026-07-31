"""Agent health monitoring with heartbeat tracking."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class HealthMonitor:
    """Monitors agent health via heartbeats and timeout detection."""

    def __init__(self) -> None:
        self._heartbeats: Dict[str, float] = {}
        self._intervals: Dict[str, float] = {}
        self._timeout_threshold: float = 30.0
        self._check_results: Dict[str, Dict[str, Any]] = {}
        self._default_interval: float = 10.0

    def register_agent(self, agent_id: str,
                       heartbeat_interval: float = 10.0) -> None:
        self._intervals[agent_id] = heartbeat_interval
        self._heartbeats[agent_id] = time.time()

    def unregister_agent(self, agent_id: str) -> bool:
        removed = agent_id in self._heartbeats
        self._heartbeats.pop(agent_id, None)
        self._intervals.pop(agent_id, None)
        self._check_results.pop(agent_id, None)
        return removed

    def record_heartbeat(self, agent_id: str) -> None:
        self._heartbeats[agent_id] = time.time()

    def set_timeout_threshold(self, seconds: float) -> None:
        self._timeout_threshold = seconds

    def check_health(self, agent_id: str) -> Dict[str, Any]:
        last = self._heartbeats.get(agent_id)
        interval = self._intervals.get(agent_id, self._default_interval)
        now = time.time()

        if last is None:
            status = "unknown"
            latency_ms = 0.0
        else:
            elapsed = now - last
            latency_ms = elapsed * 1000
            if elapsed <= interval * 2:
                status = "healthy"
            elif elapsed <= self._timeout_threshold:
                status = "degraded"
            else:
                status = "unhealthy"

        result = {
            "agent_id": agent_id,
            "status": status,
            "last_heartbeat": last,
            "latency_ms": round(latency_ms, 2),
            "timeout_threshold": self._timeout_threshold,
            "timestamp": now,
        }
        self._check_results[agent_id] = result
        return result

    def check_all(self) -> Dict[str, Dict[str, Any]]:
        results: Dict[str, Dict[str, Any]] = {}
        for aid in list(self._heartbeats.keys()):
            results[aid] = self.check_health(aid)
        return results

    def get_healthy_agents(self) -> List[str]:
        return [
            aid for aid, r in self._check_results.items()
            if r.get("status") == "healthy"
        ]

    def get_unhealthy_agents(self) -> List[str]:
        return [
            aid for aid, r in self._check_results.items()
            if r.get("status") in ("unhealthy", "degraded")
        ]

    def get_all_statuses(self) -> Dict[str, str]:
        return {
            aid: self._check_results.get(aid, {}).get("status", "unknown")
            for aid in self._heartbeats
        }

    def is_healthy(self, agent_id: str) -> bool:
        return self._check_results.get(agent_id, {}).get("status") == "healthy"

    def snapshot(self) -> Dict[str, Any]:
        return {
            "monitored_agents": len(self._heartbeats),
            "healthy": len(self.get_healthy_agents()),
            "unhealthy": len(self.get_unhealthy_agents()),
            "timeout_threshold": self._timeout_threshold,
        }
