from __future__ import annotations

import json
import time
from typing import Any

from ..monitoring_models import HealthCheckResult, HealthStatus


class HealthEndpoint:
    """Formats health check results for API responses."""

    @staticmethod
    def to_dict(
        results: dict[str, HealthCheckResult],
        include_details: bool = False,
    ) -> dict[str, Any]:
        overall = HealthStatus.HEALTHY
        components: dict[str, Any] = {}

        for name, result in results.items():
            if result.status == HealthStatus.UNHEALTHY:
                overall = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and overall != HealthStatus.UNHEALTHY:
                overall = HealthStatus.DEGRADED

            entry: dict[str, Any] = {
                "status": result.status.value,
                "latency_ms": round(result.latency_ms, 2),
                "last_checked": result.last_checked,
            }
            if result.message:
                entry["message"] = result.message
            if include_details:
                if result.dependencies:
                    entry["dependencies"] = result.dependencies
            components[name] = entry

        response: dict[str, Any] = {
            "status": overall.value,
            "timestamp": time.time(),
            "components": components,
        }
        return response

    @staticmethod
    def to_json(results: dict[str, HealthCheckResult], pretty: bool = True) -> str:
        data = HealthEndpoint.to_dict(results)
        return json.dumps(data, indent=2 if pretty else None, default=str)

    @staticmethod
    def to_text(results: dict[str, HealthCheckResult]) -> str:
        data = HealthEndpoint.to_dict(results)
        lines = [
            f"Health Status: {data['status'].upper()}",
            f"Timestamp: {data['timestamp']}",
            "",
            "Components:",
        ]
        for name, info in data["components"].items():
            lines.append(f"  [{info['status'].upper()}] {name} ({info['latency_ms']}ms)")
            if "message" in info:
                lines.append(f"    {info['message']}")
        return "\n".join(lines)
