from __future__ import annotations

import platform
import time
from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class MonitoringAgent(BaseAgent):
    async def initialize(self) -> None:
        self._status = "ready"
        self._metrics_history: list[dict[str, Any]] = []

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"

            metrics = await self._collect_metrics(context)
            self._metrics_history.append(metrics)

            alerts = self._check_alerts(metrics)
            recommendations = self._generate_recommendations(metrics, alerts)

            report = self._build_report(metrics, alerts, recommendations)

            return AgentResult(
                success=True,
                output=report,
                metrics={
                    "metrics_count": len(metrics),
                    "alerts_count": len(alerts),
                    "recommendations_count": len(recommendations),
                    "health_score": self._calculate_health_score(metrics, alerts),
                },
                artifacts={
                    "metrics": metrics,
                    "alerts": alerts,
                    "recommendations": recommendations,
                    "history_length": len(self._metrics_history),
                },
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    async def _collect_metrics(self, context: dict) -> dict[str, Any]:
        metrics: dict[str, Any] = {
            "timestamp": time.time(),
            "system": platform.system(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }

        try:
            import psutil

            metrics["cpu_percent"] = psutil.cpu_percent(interval=0.5)
            metrics["memory_percent"] = psutil.virtual_memory().percent
            metrics["disk_percent"] = psutil.disk_usage("/").percent
            metrics["network_bytes_sent"] = psutil.net_io_counters().bytes_sent
            metrics["network_bytes_recv"] = psutil.net_io_counters().bytes_recv
        except ImportError:
            metrics["cpu_percent"] = 0.0
            metrics["memory_percent"] = 0.0
            metrics["disk_percent"] = 0.0

        checks = context.get("checks", {})
        for check_name, check_fn in checks.items():
            try:
                metrics[check_name] = await check_fn()
            except Exception:
                metrics[check_name] = "error"

        return metrics

    def _check_alerts(self, metrics: dict) -> list[dict[str, Any]]:
        alerts = []
        thresholds = {
            "cpu_percent": (90, "CPU usage above 90%"),
            "memory_percent": (90, "Memory usage above 90%"),
            "disk_percent": (95, "Disk usage above 95%"),
        }
        for key, (threshold, message) in thresholds.items():
            value = metrics.get(key, 0)
            if value is not None and value > threshold:
                alerts.append(
                    {
                        "type": "critical" if value > threshold + 5 else "warning",
                        "metric": key,
                        "value": value,
                        "threshold": threshold,
                        "message": message,
                        "timestamp": time.time(),
                    }
                )
        return alerts

    def _generate_recommendations(self, metrics: dict, alerts: list) -> list[str]:
        recommendations = []
        if metrics.get("memory_percent", 0) > 80:
            recommendations.append("Consider increasing available memory or optimizing memory usage")
        if metrics.get("cpu_percent", 0) > 80:
            recommendations.append("High CPU usage detected - consider scaling horizontally")
        if metrics.get("disk_percent", 0) > 90:
            recommendations.append("Disk space running low - clean up old logs and temporary files")
        if not recommendations:
            recommendations.append("System health is good - no immediate action required")
        return recommendations

    def _calculate_health_score(self, metrics: dict, alerts: list) -> float:
        score = 100.0
        for alert in alerts:
            if alert["type"] == "critical":
                score -= 30
            else:
                score -= 15
        cpu = metrics.get("cpu_percent", 0)
        mem = metrics.get("memory_percent", 0)
        disk = metrics.get("disk_percent", 0)
        if cpu and cpu > 70:
            score -= (cpu - 70) * 0.5
        if mem and mem > 70:
            score -= (mem - 70) * 0.5
        if disk and disk > 80:
            score -= (disk - 80) * 0.5
        return max(0, min(100, score))

    def _build_report(self, metrics: dict, alerts: list, recommendations: list) -> str:
        lines = [
            "## System Monitoring Report",
            f"**Timestamp:** {time.ctime(metrics.get('timestamp', time.time()))}",
            f"**Host:** {metrics.get('hostname', 'unknown')}",
            f"**System:** {metrics.get('system', 'unknown')}",
            f"**Python:** {metrics.get('python_version', 'unknown')}",
            "",
            "### Resource Usage",
        ]

        for key in ("cpu_percent", "memory_percent", "disk_percent"):
            val = metrics.get(key, 0)
            if val:
                lines.append(f"- **{key}:** {val:.1f}%")

        if alerts:
            lines.extend(["", "### Alerts"])
            for a in alerts:
                icon = "🔴" if a["type"] == "critical" else "🟡"
                lines.append(f"- {icon} [{a['type'].upper()}] {a['message']} (value: {a['value']})")

        if recommendations:
            lines.extend(["", "### Recommendations"])
            for r in recommendations:
                lines.append(f"- {r}")

        lines.append("")
        lines.append(f"**Health Score:** {self._calculate_health_score(metrics, alerts):.1f}/100")

        return "\n".join(lines)

    def capabilities(self) -> list[str]:
        return ["system_monitoring", "resource_tracking", "alert_generation", "health_checking"]
